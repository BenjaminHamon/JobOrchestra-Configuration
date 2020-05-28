import argparse
import logging
import os
import sys

import filelock

from bhamon_orchestra_model.date_time_provider import DateTimeProvider
from bhamon_orchestra_worker.executor import Executor

import bhamon_orchestra_worker

import environment


logger = logging.getLogger("Executor")


def main():
	arguments = parse_arguments()
	environment_instance = environment.load_environment()
	environment.configure_logging(environment_instance, arguments)

	environment_instance["orchestra_worker_configuration"] = os.path.join(os.getcwd(), "worker.json").replace("\\", "/")
	environment_instance["orchestra_worker_python_executable"] = sys.executable.replace("\\", "/")

	with filelock.FileLock(os.path.join("runs", arguments.run_identifier, "executor.lock"), 5):
		logger.info("(%s) Job Orchestra %s", arguments.run_identifier, bhamon_orchestra_worker.__version__)
		executor_instance = create_application(arguments)
		executor_instance.run(environment_instance)


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("run_identifier", help = "set the run identifier")
	return argument_parser.parse_args()


def create_application(arguments):
	date_time_provider_instance = DateTimeProvider()

	executor_instance = Executor(
		run_identifier = arguments.run_identifier,
		date_time_provider = date_time_provider_instance,
	)

	return executor_instance


if __name__ == "__main__":
	main()
