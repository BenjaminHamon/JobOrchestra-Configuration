import copy
import json
import logging
import os
import platform
import sys


def create_default_environment():
	return {
		"logging_stream_level": "info",
		"logging_stream_format": "[{levelname}][{name}] {message}",
		"logging_stream_date_format": "%Y-%m-%dT%H:%M:%S",
		"logging_stream_traceback": False,

		"logging_file_level": "debug",
		"logging_file_format": "[{levelname}][{name}] {message}",
		"logging_file_date_format": "%Y-%m-%dT%H:%M:%S",
		"logging_file_traceback": True,
		"logging_file_mode": "w",
		"logging_file_paths": [],

		"logging_summary_format": "[{levelname}][{name}] {message}",
		"logging_summary_date_format": "%Y-%m-%dT%H:%M:%S",

		"git_executable": "git",
		"python3_system_executable": find_system_python(),
	}


def load_environment():
	# Default + User (+ Local)
	# The local transform is ignored here because worker scripts are overwriting it

	default_environment = create_default_environment()

	environment_instance = copy.deepcopy(default_environment)
	environment_instance.update(_load_environment_transform(os.path.join(os.path.expanduser("~"), "environment.json")))
	# environment_instance.update(_load_environment_transform("environment.json"))

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


def find_system_python():
	if platform.system() == "Linux":
		return "/usr/bin/python3"

	if platform.system() == "Windows":
		possible_paths = [
			os.path.join(os.environ["SystemDrive"] + "\\", "Python38", "python.exe"),
			os.path.join(os.environ["ProgramFiles"], "Python38", "python.exe"),
			os.path.join(os.environ["SystemDrive"] + "\\", "Python37", "python.exe"),
			os.path.join(os.environ["ProgramFiles"], "Python37", "python.exe"),
			os.path.join(os.environ["SystemDrive"] + "\\", "Python36", "python.exe"),
			os.path.join(os.environ["ProgramFiles"], "Python36", "python.exe"),
			os.path.join(os.environ["SystemDrive"] + "\\", "Python35", "python.exe"),
			os.path.join(os.environ["ProgramFiles"], "Python35", "python.exe"),
		]

		for path in possible_paths:
			if os.path.exists(path):
				return path

		return None

	raise ValueError("Unsupported platform: '%s'" % platform.system())
