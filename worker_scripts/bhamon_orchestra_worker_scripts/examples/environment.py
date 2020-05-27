import argparse
import json
import logging
import os
import platform
import subprocess

import bhamon_orchestra_worker_scripts.environment as environment


logger = logging.getLogger("Main")


def main():
	environment.configure_logging(logging.INFO)
	environment_instance = environment.load_environment()

	arguments = parse_arguments()
	with open(arguments.configuration, mode = "r", encoding = "utf-8") as configuration_file:
		worker_configuration = json.load(configuration_file)

	# Prevent active pyvenv from overriding a python executable specified in a command
	if "__PYVENV_LAUNCHER__" in os.environ:
		del os.environ["__PYVENV_LAUNCHER__"]

	setup_virtual_environment(environment_instance["python3_system_executable"])
	print("")
	show_worker_environment(environment_instance)
	print("")
	show_worker_configuration(worker_configuration)
	print("")


def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--configuration", required = True, metavar = "<path>", help = "set the worker configuration file path")
	return parser.parse_args()


def setup_virtual_environment(python_system_executable):
	logger.info("Setting up python virtual environment")

	setup_venv_command = [ python_system_executable, "-m", "venv", ".venv" ]
	logger.info("+ %s", " ".join(setup_venv_command))
	subprocess.check_call(setup_venv_command)

	if platform.system() == "Linux" and not os.path.exists(".venv/scripts"):
		os.symlink("bin", ".venv/scripts")

	install_pip_command = [ ".venv/scripts/python", "-m", "pip", "install", "--upgrade", "pip" ]
	logger.info("+ %s", " ".join(install_pip_command))
	subprocess.check_call(install_pip_command)


def show_worker_environment(worker_environment):
	logger.info("Worker Environment")
	for key, value in worker_environment.items():
		logger.info("%s: '%s'", key, value)


def show_worker_configuration(worker_configuration):
	logger.info("Worker Configuration")
	for key, value in worker_configuration.items():
		logger.info("%s: '%s'", key, value)


if __name__ == "__main__":
	main()
