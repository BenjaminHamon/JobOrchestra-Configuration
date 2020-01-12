import argparse
import json
import logging
import os
import platform
import re
import subprocess

from bhamon_orchestra_model.revision_control.github import GitHubClient
from bhamon_orchestra_worker.revision_control.git import GitClient
import bhamon_orchestra_worker.workspace

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

	if arguments.type == "controller":
		resolve_controller_revision(arguments.repository, arguments.revision, arguments.results)

	elif arguments.type == "worker":
		git_client_instance = GitClient(environment_instance["git_executable"])

		setup_virtual_environment(environment_instance)
		print("")
		configure_workspace_environment(environment_instance, worker_configuration)
		print("")
		git_client_instance.initialize(arguments.repository)
		print("")
		git_client_instance.update(arguments.revision, arguments.results)
		print("")


def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--configuration", required = True, metavar = "<path>", help = "set the worker configuration file path")
	parser.add_argument("--type", required = True, choices = [ "controller", "worker" ], help = "set the workspace type (controller, worker)")
	parser.add_argument("--repository", required = True, metavar = "<uri>", help = "set the repository uri to clone")
	parser.add_argument("--revision", required = True, metavar = "<revision>", help = "set the revision to update to")
	parser.add_argument("--results", required = True, metavar = "<path>", help = "set the file path where to store the run results")
	return parser.parse_args()


def setup_virtual_environment(environment_instance):
	logger.info("Setting up python virtual environment")

	setup_venv_command = [ environment_instance["python3_system_executable"], "-m", "venv", ".venv" ]
	logger.info("+ %s", " ".join(setup_venv_command))
	subprocess.check_call(setup_venv_command)

	if platform.system() == "Linux" and not os.path.exists(".venv/scripts"):
		os.symlink("bin", ".venv/scripts")

	install_pip_command = [ ".venv/scripts/python", "-m", "pip", "install", "--upgrade", "pip" ]
	logger.info("+ %s", " ".join(install_pip_command))
	subprocess.check_call(install_pip_command)


def configure_workspace_environment(environment_instance, worker_configuration):
	logger.info("Configuring workspace environment")

	workspace_environment = {
		"artifact_server_url": worker_configuration["artifact_server_url"],
		"artifact_server_parameters": worker_configuration["artifact_server_parameters"],
		"git_executable": environment_instance["git_executable"],
		"unity_2019_executable": environment_instance["unity_2019_executable"],
	}

	for key, value in workspace_environment.items():
		logger.info("%s: '%s'", key, value)

	with open("environment.json", "w") as workspace_environment_file:
		json.dump(workspace_environment, workspace_environment_file, indent = 4)


def resolve_controller_revision(repository, revision, result_file_path):
	github_client_instance = GitHubClient()
	match = re.search(r"^https://github.com/(?P<repository>[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+)$", repository)
	revision_data = github_client_instance.get_revision(match.group("repository"), revision)

	results = bhamon_orchestra_worker.workspace.load_results(result_file_path)
	results["revision_control"] = { "revision": revision_data["identifier"], "date": revision_data["date"] }
	bhamon_orchestra_worker.workspace.save_results(result_file_path, results)

	logger.info("Revision: '%s' (%s)", revision_data["identifier"], revision_data["date"])


if __name__ == "__main__":
	main()
