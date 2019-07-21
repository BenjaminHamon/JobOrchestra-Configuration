import argparse
import json
import logging
import platform
import os
import subprocess

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
		"python3_executable": ".venv/scripts/python",
		"python_package_repository": environment_instance["python_package_repository"],
	}

	for key, value in workspace_environment.items():
		logger.info("%s: '%s'", key, value)

	with open("environment.json", "w") as workspace_environment_file:
		json.dump(workspace_environment, workspace_environment_file, indent = 4)


if __name__ == "__main__":
	main()
