import glob
import logging
import os
import subprocess


logger = logging.getLogger("Main")


def configure_argument_parser(environment, configuration, subparsers): # pylint: disable=unused-argument
	return subparsers.add_parser("lint", help = "run linter")


def run(environment, configuration, arguments): # pylint: disable=unused-argument
	lint_packages(environment["python3_executable"], configuration["components"])
	lint_scripts(environment["python3_executable"], "entry_points")
	lint_scripts(environment["python3_executable"], "worker_scripts")


def lint_packages(python_executable, component_collection):
	logger.info("Running linter in python packages")

	pylint_command = [ python_executable, "-m", "pylint" ]
	pylint_command += [ component["path"] for component in component_collection ]

	logger.info("+ %s", " ".join(pylint_command))
	subprocess.check_call(pylint_command)


def lint_scripts(python_executable, directory):
	logger.info("Running linter in '%s'", directory)

	pylint_command = [ python_executable, "-m", "pylint" ]
	pylint_command += [ file_path for file_path in glob.glob(os.path.join(directory, "**", "*.py"), recursive = True) ]

	logger.info("+ %s", " ".join(pylint_command))
	subprocess.check_call(pylint_command)
