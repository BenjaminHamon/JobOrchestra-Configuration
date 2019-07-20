import argparse
import json
import logging
import os

import filelock

import bhamon_build_worker.worker as worker

import environment


def main():
	environment.configure_logging(logging.INFO)
	arguments = parse_arguments()
	executor_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "executor_main.py"))

	with open(arguments.configuration, "r") as configuration_file:
		configuration = json.load(configuration_file)

	os.chdir(configuration["build_workers"][arguments.identifier]["working_directory"])
	with filelock.FileLock("build_worker.lock", 5):
		worker.run(configuration["build_master_url"], arguments.identifier, executor_script)


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--identifier", required = True, help = "set the identifier for this worker")
	argument_parser.add_argument("--configuration", default = "build_service.json", help = "set the configuration file path")
	return argument_parser.parse_args()


if __name__ == "__main__":
	main()
