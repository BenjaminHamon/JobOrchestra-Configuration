import copy
import json
import logging
import os
import platform


log_format = "[{levelname}][{name}] {message}"


def configure_logging(log_level):
	logging.basicConfig(level = log_level, format = log_format, style = "{")
	logging.addLevelName(logging.DEBUG, "Debug")
	logging.addLevelName(logging.INFO, "Info")
	logging.addLevelName(logging.WARNING, "Warning")
	logging.addLevelName(logging.ERROR, "Error")
	logging.addLevelName(logging.CRITICAL, "Critical")


def create_default_environment():
	return {
		"git_executable": "git",
		"python3_system_executable": find_system_python(),
	}


def load_environment():
	# Default + User (+ Local)
	# The local transform is ignored here because worker scripts are overwriting it

	default_environment = create_default_environment()

	environment_instance = copy.deepcopy(create_default_environment())
	environment_instance.update(_load_environment_transform(os.path.join(os.path.expanduser("~"), "environment.json")))
	# environment_instance.update(_load_environment_transform("environment.json"))

	for key in environment_instance.keys():
		if environment_instance[key] == "$default":
			environment_instance[key] = default_environment[key]

	return environment_instance


def _load_environment_transform(transform_file_path):
	if not os.path.exists(transform_file_path):
		return {}
	with open(transform_file_path) as transform_file:
		return json.load(transform_file)


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
