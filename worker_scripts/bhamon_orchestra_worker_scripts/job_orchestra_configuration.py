import argparse
import json
import logging
import os

from bhamon_orchestra_worker.revision_control.git import GitClient

import bhamon_orchestra_worker_scripts.environment as environment
import bhamon_orchestra_worker_scripts.helpers.python as python_helpers


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

	git_client_instance = GitClient(environment_instance["git_executable"])

	python_helpers.setup_virtual_environment(environment_instance["python3_system_executable"])
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


def configure_workspace_environment(worker_configuration):
	logger.info("Configuring workspace environment")

	workspace_environment = {
		"python3_executable": ".venv/scripts/python",
		"artifact_server_url": worker_configuration["artifact_server_url"],
		"artifact_server_parameters": worker_configuration["artifact_server_parameters"],
		"python_package_repository_url": worker_configuration["python_package_repository_url"],
		"python_package_repository_parameters": worker_configuration["python_package_repository_parameters"],
		"python_package_repository_web_url": worker_configuration["python_package_repository_web_url"],
	}

	for key, value in workspace_environment.items():
		logger.info("%s: '%s'", key, value)

	with open("environment.json", mode = "w", encoding = "utf-8") as workspace_environment_file:
		json.dump(workspace_environment, workspace_environment_file, indent = 4)


if __name__ == "__main__":
	main()
