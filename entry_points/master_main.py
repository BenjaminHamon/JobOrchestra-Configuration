import argparse
import functools
import importlib
import json
import logging

import filelock

from bhamon_orchestra_master.job_scheduler import JobScheduler
from bhamon_orchestra_master.master import Master
from bhamon_orchestra_master.protocol import WebSocketServerProtocol
from bhamon_orchestra_master.supervisor import Supervisor
from bhamon_orchestra_master.task_processor import TaskProcessor
from bhamon_orchestra_model.authentication_provider import AuthenticationProvider
from bhamon_orchestra_model.authorization_provider import AuthorizationProvider
from bhamon_orchestra_model.database.file_storage import FileStorage
from bhamon_orchestra_model.job_provider import JobProvider
from bhamon_orchestra_model.project_provider import ProjectProvider
from bhamon_orchestra_model.run_provider import RunProvider
from bhamon_orchestra_model.task_provider import TaskProvider
from bhamon_orchestra_model.user_provider import UserProvider
from bhamon_orchestra_model.worker_provider import WorkerProvider

from bhamon_orchestra_configuration.worker_selector import WorkerSelector

import environment
import master_configuration


def main():
	environment.configure_logging(logging.INFO)
	arguments = parse_arguments()

	with open(arguments.configuration, "r") as configuration_file:
		configuration = json.load(configuration_file)
	environment.configure_log_file(configuration["orchestra_master_log_file_path"], logging.INFO)

	with filelock.FileLock("master.lock", 5):
		application = create_application(configuration)
		application.run()


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--configuration", default = "orchestra.json", metavar = "<path>", help = "set the configuration file path")
	return argument_parser.parse_args()


def create_application(configuration): # pylint: disable = too-many-locals
	environment_instance = {
		"artifact_server_url": configuration["artifact_server_web_url"],
		"python_package_repository_url": configuration["python_package_repository_web_url"],
	}

	database_client_instance = environment.create_database_client(configuration["orchestra_database_uri"], configuration["orchestra_database_authentication"])
	file_storage_instance = FileStorage(configuration["orchestra_file_storage_path"])

	authentication_provider_instance = AuthenticationProvider(database_client_instance)
	authorization_provider_instance = AuthorizationProvider()
	job_provider_instance = JobProvider(database_client_instance)
	project_provider_instance = ProjectProvider(database_client_instance)
	run_provider_instance = RunProvider(database_client_instance, file_storage_instance)
	task_provider_instance = TaskProvider(database_client_instance)
	user_provider_instance = UserProvider(database_client_instance)
	worker_provider_instance = WorkerProvider(database_client_instance)

	task_processor_instance = TaskProcessor(
		task_provider = task_provider_instance,
	)

	worker_selector_instance = WorkerSelector(
		worker_provider = worker_provider_instance,
	)

	protocol_factory = functools.partial(
		WebSocketServerProtocol,
		user_provider = user_provider_instance,
		authentication_provider = authentication_provider_instance,
		authorization_provider = authorization_provider_instance,
	)

	supervisor_instance = Supervisor(
		host = configuration["orchestra_master_listen_address"],
		port = configuration["orchestra_master_listen_port"],
		worker_provider = worker_provider_instance,
		run_provider = run_provider_instance,
		protocol_factory = protocol_factory,
	)

	job_scheduler_instance = JobScheduler(
		supervisor = supervisor_instance,
		job_provider = job_provider_instance,
		run_provider = run_provider_instance,
		worker_selector = worker_selector_instance,
	)

	configuration_loader = functools.partial(reload_configuration, environment_instance = environment_instance)

	master_instance = Master(
		job_scheduler = job_scheduler_instance,
		supervisor = supervisor_instance,
		task_processor = task_processor_instance,
		project_provider = project_provider_instance,
		job_provider = job_provider_instance,
		worker_provider = worker_provider_instance,
		configuration_loader = configuration_loader,
	)

	master_instance.register_default_tasks()

	return master_instance


def reload_configuration(environment_instance):
	importlib.reload(master_configuration)
	master_configuration.reload_modules()
	return master_configuration.configure(environment_instance)


if __name__ == "__main__":
	main()
