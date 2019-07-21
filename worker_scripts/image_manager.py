import argparse
import json
import logging
import os
import platform
import re
import subprocess

import bhamon_build_worker.workspace

import bhamon_build_model_extensions.revision_control.github as github
import bhamon_build_worker_extensions.revision_control.git as git

import environment


logger = logging.getLogger("Main")


def main():
	environment.configure_logging(logging.INFO)
	environment_instance = environment.load_environment()

	arguments = parse_arguments()

	# Prevent active pyvenv from overriding a python executable specified in a command
	if "__PYVENV_LAUNCHER__" in os.environ:
		del os.environ["__PYVENV_LAUNCHER__"]

	if arguments.type == "controller":
		resolve_controller_revision(arguments.repository, arguments.revision, arguments.results)

	elif arguments.type == "worker":
		setup_virtual_environment(environment_instance)
		print("")
		configure_workspace_environment(environment_instance)
		print("")
		git.initialize(environment_instance, arguments.repository)
		print("")
		git.update(environment_instance, arguments.revision, arguments.results)
		print("")


def parse_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("--type", required = True, choices = [ "controller", "worker" ], help = "set the workspace type (controller, worker)")
	parser.add_argument("--repository", required = True, help = "set the repository uri to clone")
	parser.add_argument("--revision", required = True, help = "set the revision to update to")
	parser.add_argument("--results", required = True, help = "set the file path where to store the build results")
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


def configure_workspace_environment(environment_instance):
	logger.info("Configuring workspace environment")

	workspace_environment = {
		"artifact_repository": environment_instance["artifact_repository"],
		"git_executable": environment_instance["git_executable"],
		"msbuild_2017_executable": environment_instance["msbuild_2017_executable"],
		"nuget_executable": environment_instance["nuget_executable"],
		"python3_executable": ".venv/scripts/python",
		"vstest_2017_executable": environment_instance["vstest_2017_executable"],
	}

	for key, value in workspace_environment.items():
		logger.info("%s: '%s'", key, value)

	with open("environment.json", "w") as workspace_environment_file:
		json.dump(workspace_environment, workspace_environment_file, indent = 4)


def resolve_controller_revision(repository, revision, result_file_path):
	match = re.search(r"^https://github.com/(?P<owner>[a-zA-Z0-9_\-\.]+)/(?P<repository>[a-zA-Z0-9_\-\.]+)$", repository)
	revision_data = github.get_revision(match.group("owner"), match.group("repository"), revision)

	results = bhamon_build_worker.workspace.load_results(result_file_path)
	results["revision_control"] = { "revision": revision_data["identifier"], "date": revision_data["date"] }
	bhamon_build_worker.workspace.save_results(result_file_path, results)

	logger.info("Revision: '%s' (%s)", revision_data["identifier"], revision_data["date"])


if __name__ == "__main__":
	main()
