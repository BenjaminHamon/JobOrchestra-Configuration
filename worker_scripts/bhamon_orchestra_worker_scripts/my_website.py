import argparse
import json
import logging
import platform
import os
import subprocess

from bhamon_orchestra_worker.revision_control.git import GitClient

import bhamon_orchestra_worker_scripts.environment as environment


logger = logging.getLogger("Main")


def main():
	environment.configure_logging(logging.INFO)
	environment_instance = environment.load_environment()

	arguments = parse_arguments()
	with open(arguments.configuration, "r") as configuration_file:
		worker_configuration = json.load(configuration_file)

	# Prevent active pyvenv from overriding a python executable specified in a command
	if "__PYVENV_LAUNCHER__" in os.environ:
		del os.environ["__PYVENV_LAUNCHER__"]

	git_client_instance = GitClient(environment_instance["git_executable"])

	setup_virtual_environment(environment_instance["python3_system_executable"])
	print("")
	configure_workspace_environment(worker_configuration)
	print("")
	git_client_instance.initialize(arguments.repository)
	print("")
	git_client_instance.update(arguments.revision, arguments.results)
	print("")


def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--configuration", required = True, metavar = "<path>", help = "set the worker configuration file path")
	parser.add_argument("--repository", required = True, metavar = "<uri>", help = "set the repository uri to clone")
	parser.add_argument("--revision", required = True, metavar = "<revision>", help = "set the revision to update to")
	parser.add_argument("--results", required = True, metavar = "<path>", help = "set the file path where to store the run results")
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


def configure_workspace_environment(worker_configuration):
	logger.info("Configuring workspace environment")

	workspace_environment = {
		"python3_executable": ".venv/scripts/python",
		"artifact_server_url": worker_configuration["artifact_server_url"],
		"artifact_server_parameters": worker_configuration["artifact_server_parameters"],
		"python_package_repository_url": worker_configuration["python_package_repository_url"],
		"python_package_repository_parameters": worker_configuration["python_package_repository_parameters"],
	}

	for key, value in workspace_environment.items():
		logger.info("%s: '%s'", key, value)

	with open("environment.json", "w") as workspace_environment_file:
		json.dump(workspace_environment, workspace_environment_file, indent = 4)


if __name__ == "__main__":
	main()
