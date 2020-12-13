import argparse
import json
import logging
import os
import sys

import filelock

from bhamon_orchestra_model.application import AsyncioApplication
from bhamon_orchestra_model.database.file_data_storage import FileDataStorage
from bhamon_orchestra_model.date_time_provider import DateTimeProvider

import bhamon_orchestra_worker
from bhamon_orchestra_worker.job_executor import JobExecutor
from bhamon_orchestra_worker.worker_storage import WorkerStorage
from bhamon_orchestra_worker.pipeline_executor import PipelineExecutor
from bhamon_orchestra_worker.web_service_client import WebServiceClient

import environment


logger = logging.getLogger("Main")


def main():
	arguments = parse_arguments()
	environment_instance = environment.load_environment()
	environment.configure_logging(environment_instance, arguments)

	environment_instance["orchestra_worker_configuration"] = os.path.join(os.getcwd(), "worker.json").replace("\\", "/")
	environment_instance["orchestra_worker_python_executable"] = sys.executable.replace("\\", "/")

	application_title = bhamon_orchestra_worker.__product__ + " " + "Executor"
	application_version = bhamon_orchestra_worker.__version__

	with open(arguments.configuration, mode = "r", encoding = "utf-8") as configuration_file:
		configuration = json.load(configuration_file)
	with open(configuration["authentication_file_path"], mode = "r", encoding = "utf-8") as authentication_file:
		authentication = json.load(authentication_file)

	with filelock.FileLock(os.path.join("runs", arguments.run_identifier, "executor.lock"), 5):
		executor_instance = create_application(arguments.run_identifier, configuration, authentication)
		asyncio_application = AsyncioApplication(application_title, application_version)
		asyncio_application.run_as_standalone(executor_instance.run(arguments.run_identifier, environment_instance))


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("run_identifier", help = "set the run identifier")
	argument_parser.add_argument("--configuration", default = "worker.json", metavar = "<path>", help = "set the configuration file path")
	return argument_parser.parse_args()


def create_application(run_identifier, configuration, authentication):
	data_storage_instance = FileDataStorage(".")
	date_time_provider_instance = DateTimeProvider()
	worker_storage_instance = WorkerStorage(data_storage_instance)
	service_client_instance = WebServiceClient(configuration["orchestra_service_url"], authorization = (authentication["user"], authentication["secret"]))

	request = worker_storage_instance.load_request(run_identifier)

	if request["job_definition"]["type"] == "job":
		executor_instance = JobExecutor(
			storage = worker_storage_instance,
			date_time_provider = date_time_provider_instance,
		)

	elif request["job_definition"]["type"] == "pipeline":
		executor_instance = PipelineExecutor(
			storage = worker_storage_instance,
			date_time_provider = date_time_provider_instance,
			service_client = service_client_instance,
		)

	else:
		raise RuntimeError("Unsupported job definition")

	return executor_instance


if __name__ == "__main__":
	main()
