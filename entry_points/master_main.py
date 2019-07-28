import argparse
import importlib
import json
import logging

import filelock

from bhamon_build_configuration.worker_selector import WorkerSelector
from bhamon_build_master.master import Master
from bhamon_build_master.supervisor import Supervisor
from bhamon_build_master.task_processor import TaskProcessor
from bhamon_build_model.build_provider import BuildProvider
from bhamon_build_model.file_storage import FileStorage
from bhamon_build_model.job_provider import JobProvider
from bhamon_build_model.task_provider import TaskProvider
from bhamon_build_model.worker_provider import WorkerProvider

import environment
import master_configuration


def main():
	environment.configure_logging(logging.INFO)
	arguments = parse_arguments()

	with open(arguments.configuration, "r") as configuration_file:
		configuration = json.load(configuration_file)
	environment.configure_log_file(configuration["build_master_log_file_path"], logging.INFO)

	with filelock.FileLock("build_master.lock", 5):
		application = create_application(configuration)
		application.run()


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--configuration", default = "build_service.json", help = "set the configuration file path")
	return argument_parser.parse_args()


def create_application(configuration):
	database_client_instance = environment.create_database_client(configuration["build_database_uri"], configuration["build_database_authentication"])
	file_storage_instance = FileStorage(configuration["build_file_storage_path"])

	build_provider_instance = BuildProvider(database_client_instance, file_storage_instance)
	job_provider_instance = JobProvider(database_client_instance)
	task_provider_instance = TaskProvider(database_client_instance)
	worker_provider_instance = WorkerProvider(database_client_instance)

	task_processor_instance = TaskProcessor(
		task_provider = task_provider_instance,
	)

	worker_selector_instance = WorkerSelector(
		worker_provider = worker_provider_instance,
	)

	supervisor_instance = Supervisor(
		host = configuration["build_master_listen_address"],
		port = configuration["build_master_listen_port"],
		worker_provider = worker_provider_instance,
		job_provider = job_provider_instance,
		build_provider = build_provider_instance,
		worker_selector = worker_selector_instance,
	)

	master_instance = Master(
		supervisor = supervisor_instance,
		task_processor = task_processor_instance,
		job_provider = job_provider_instance,
		worker_provider = worker_provider_instance,
		configuration_loader = reload_configuration,
	)

	master_instance.register_default_tasks()

	return master_instance


def reload_configuration():
	importlib.reload(master_configuration)
	master_configuration.reload_modules()
	return master_configuration.configure()


if __name__ == "__main__":
	main()
