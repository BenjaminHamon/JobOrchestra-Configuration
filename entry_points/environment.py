import copy
import json
import logging
import os
import re
import sys

import pymongo
import sqlalchemy

from bhamon_orchestra_model.database.json_database_administration import JsonDatabaseAdministration
from bhamon_orchestra_model.database.json_database_client import JsonDatabaseClient
from bhamon_orchestra_model.database.mongo_database_administration import MongoDatabaseAdministration
from bhamon_orchestra_model.database.mongo_database_client import MongoDatabaseClient
from bhamon_orchestra_model.database.sql_database_administration import SqlDatabaseAdministration
from bhamon_orchestra_model.database.sql_database_client import SqlDatabaseClient


all_log_levels = [ "debug", "info", "warning", "error", "critical" ]


def create_default_environment():
	return {
		"logging_stream_level": "info",
		"logging_stream_format": "{asctime} [{levelname}][{name}] {message}",
		"logging_stream_date_format": "%Y-%m-%dT%H:%M:%S",
		"logging_stream_traceback": False,

		"logging_file_level": "info",
		"logging_file_format": "{asctime} [{levelname}][{name}] {message}",
		"logging_file_date_format": "%Y-%m-%dT%H:%M:%S",
		"logging_file_traceback": True,
		"logging_file_mode": "a",
		"logging_file_paths": [],
	}


def load_environment():
	default_environment = create_default_environment()

	environment_instance = copy.deepcopy(default_environment)
	environment_instance.update(_load_environment_transform(os.path.join(os.path.expanduser("~"), "environment.json")))
	environment_instance.update(_load_environment_transform("environment.json"))

	for key in environment_instance.keys():
		if environment_instance[key] == "$default":
			environment_instance[key] = default_environment[key]

	return environment_instance


def _load_environment_transform(transform_file_path):
	if not os.path.exists(transform_file_path):
		return {}
	with open(transform_file_path, mode = "r", encoding = "utf-8") as transform_file:
		return json.load(transform_file)


def configure_logging(environment_instance, arguments):
	if arguments is not None and getattr(arguments, "verbosity", None) is not None:
		environment_instance["logging_stream_level"] = arguments.verbosity
	if arguments is not None and getattr(arguments, "verbosity", None) == "debug":
		environment_instance["logging_stream_traceback"] = True
	if arguments is not None and getattr(arguments, "log_file_verbosity", None) is not None:
		environment_instance["logging_file_level"] = arguments.log_file_verbosity
	if arguments is not None and getattr(arguments, "log_file", None) is not None:
		environment_instance["logging_file_paths"].append(arguments.log_file)

	environment_instance["logging_stream_levelno"] = logging.getLevelName(environment_instance["logging_stream_level"].upper())
	environment_instance["logging_file_levelno"] = logging.getLevelName(environment_instance["logging_file_level"].upper())

	logging.addLevelName(logging.DEBUG, "Debug")
	logging.addLevelName(logging.INFO, "Info")
	logging.addLevelName(logging.WARNING, "Warning")
	logging.addLevelName(logging.ERROR, "Error")
	logging.addLevelName(logging.CRITICAL, "Critical")

	logging.root.setLevel(logging.DEBUG)
	logging.getLogger("asyncio").setLevel(logging.INFO)
	logging.getLogger("filelock").setLevel(logging.WARNING)
	logging.getLogger("urllib3").setLevel(logging.INFO)
	logging.getLogger("websockets.protocol").setLevel(logging.INFO)
	logging.getLogger("werkzeug").setLevel(logging.WARNING)

	configure_log_stream(environment_instance, sys.stdout)
	for log_file_path in environment_instance["logging_file_paths"]:
		configure_log_file(environment_instance, log_file_path)


def configure_log_stream(environment_instance, stream):
	formatter = logging.Formatter(environment_instance["logging_stream_format"], environment_instance["logging_stream_date_format"], "{")
	stream_handler = logging.StreamHandler(stream)
	stream_handler.setLevel(environment_instance["logging_stream_levelno"])
	stream_handler.formatter = formatter
	logging.root.addHandler(stream_handler)


def configure_log_file(environment_instance, file_path):
	if os.path.dirname(file_path):
		os.makedirs(os.path.dirname(file_path), exist_ok = True)

	formatter = logging.Formatter(environment_instance["logging_file_format"], environment_instance["logging_file_date_format"], "{")
	file_handler = logging.FileHandler(file_path, mode = environment_instance["logging_file_mode"], encoding = "utf-8")
	file_handler.setLevel(environment_instance["logging_file_levelno"])
	file_handler.formatter = formatter
	logging.root.addHandler(file_handler)


def create_database_administration_factory(database_uri, database_authentication, database_metadata):
	if database_uri.startswith("json://"):
		return lambda: JsonDatabaseAdministration(re.sub("^json://", "", database_uri))
	if database_uri.startswith("mongodb://"):
		return lambda: MongoDatabaseAdministration(pymongo.MongoClient(database_uri, **database_authentication))
	if database_uri.startswith("postgresql://"):
		database_engine = sqlalchemy.create_engine(database_uri)
		return lambda: SqlDatabaseAdministration(database_engine.connect(), database_metadata)
	raise ValueError("Unsupported database uri '%s'" % database_uri)


def create_database_client_factory(database_uri, database_authentication, database_metadata):
	if database_uri.startswith("json://"):
		return lambda: JsonDatabaseClient(re.sub("^json://", "", database_uri))
	if database_uri.startswith("mongodb://"):
		return lambda: MongoDatabaseClient(pymongo.MongoClient(database_uri, **database_authentication))
	if database_uri.startswith("postgresql://"):
		database_engine = sqlalchemy.create_engine(database_uri)
		return lambda: SqlDatabaseClient(database_engine.connect(), database_metadata)
	raise ValueError("Unsupported database uri '%s'" % database_uri)
