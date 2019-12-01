import copy
import json
import logging
import os
import re
import sys

import pymongo

from bhamon_build_model.database.json_database_client import JsonDatabaseClient
from bhamon_build_model.database.mongo_database_client import MongoDatabaseClient


stdout_log_format = "[{levelname}][{name}] {message}"
file_log_format = "{asctime} [{levelname}][{name}] {message}"
date_format = "%Y-%m-%dT%H:%M:%S"


def configure_logging(log_level):
	logging.root.setLevel(log_level)

	logging.addLevelName(logging.DEBUG, "Debug")
	logging.addLevelName(logging.INFO, "Info")
	logging.addLevelName(logging.WARNING, "Warning")
	logging.addLevelName(logging.ERROR, "Error")
	logging.addLevelName(logging.CRITICAL, "Critical")

	logging.getLogger("asyncio").setLevel(logging.INFO)
	logging.getLogger("filelock").setLevel(logging.WARNING)
	logging.getLogger("urllib3").setLevel(logging.INFO)
	logging.getLogger("websockets.protocol").setLevel(logging.INFO)
	logging.getLogger("werkzeug").setLevel(logging.WARNING)

	log_formatter = logging.Formatter(stdout_log_format, date_format, "{")
	stream_handler = logging.StreamHandler(sys.stdout)
	stream_handler.setLevel(log_level)
	stream_handler.formatter = log_formatter
	logging.root.addHandler(stream_handler)


def configure_log_file(log_file_path, log_level):
	log_formatter = logging.Formatter(file_log_format, date_format, "{")
	log_handler = logging.FileHandler(log_file_path)
	log_handler.setLevel(log_level)
	log_handler.setFormatter(log_formatter)
	logging.root.addHandler(log_handler)


def create_database_client(database_uri, database_authentication):
	if database_uri.startswith("json://"):
		return JsonDatabaseClient(re.sub("^json://", "", database_uri))
	if database_uri.startswith("mongodb://"):
		return MongoDatabaseClient(pymongo.MongoClient(database_uri, **database_authentication).get_database())
	raise ValueError("Unsupported database uri '%s'" % database_uri)


def create_default_environment():
	return {}


def load_environment():
	default_environment = create_default_environment()

	environment_instance = copy.deepcopy(create_default_environment())
	environment_instance.update(load_transform(os.path.join(os.path.expanduser("~"), "environment.json")))
	environment_instance.update(load_transform("environment.json"))

	for key in environment_instance.keys():
		if environment_instance[key] == "$default":
			environment_instance[key] = default_environment[key]

	return environment_instance


def load_transform(transform_file_path):
	if not os.path.exists(transform_file_path):
		return {}
	with open(transform_file_path) as transform_file:
		return json.load(transform_file)
