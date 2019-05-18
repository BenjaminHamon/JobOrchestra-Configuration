import copy
import json
import logging
import os
import sys


log_format = "[{levelname}][{name}] {message}"


def configure_logging(log_level):
	logging.basicConfig(level = log_level, format = log_format, style = "{")
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


def create_default_environment():
	return {
		"python3_executable": sys.executable,
	}


def load_environment():
	default_environment = create_default_environment()

	environment_instance = copy.deepcopy(create_default_environment())
	environment_instance.update(_load_environment_transform(os.path.join(os.path.expanduser("~"), "environment.json")))
	environment_instance.update(_load_environment_transform(os.path.join(os.path.dirname(__file__), "environment.json")))
	environment_instance.update(_load_environment_transform("environment.json"))

	for key in environment_instance.keys():
		if environment_instance[key] == "$default":
			environment_instance[key] = default_environment[key]

	return environment_instance


def _load_environment_transform(transform_file_path):
	if not os.path.exists(transform_file_path):
		return {}
	with open(transform_file_path) as transform_file:
		return json.load(transform_file)
