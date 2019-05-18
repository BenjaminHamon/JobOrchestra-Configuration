import logging
import os
import shutil


logger = logging.getLogger("Main")


def configure_argument_parser(environment, configuration, subparsers): # pylint: disable=unused-argument
	return subparsers.add_parser("clean", help = "clean the workspace")


def run(environment, configuration, arguments): # pylint: disable=unused-argument
	clean(configuration, arguments.simulate)


def clean(configuration, simulate):
	logger.info("Cleaning the workspace")
	print("")

	directories_to_clean = []

	for component in configuration["components"]:
		for package in component["packages"]:
			directories_to_clean.append(os.path.join(component["path"], package, "__pycache__"))
			directories_to_clean.append(os.path.join(component["path"], package + ".egg-info"))

	directories_to_clean.sort()

	for directory in directories_to_clean:
		if os.path.exists(directory):
			logger.info("Removing directory '%s'", directory)
			if not simulate:
				shutil.rmtree(directory)
