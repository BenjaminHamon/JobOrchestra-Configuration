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
from bhamon_orchestra_model.authentication_provider import AuthenticationProvider
from bhamon_orchestra_model.authorization_provider import AuthorizationProvider
from bhamon_orchestra_model.database.file_storage import FileStorage
from bhamon_orchestra_model.date_time_provider import DateTimeProvider
from bhamon_orchestra_model.job_provider import JobProvider
from bhamon_orchestra_model.project_provider import ProjectProvider
from bhamon_orchestra_model.run_provider import RunProvider
from bhamon_orchestra_model.schedule_provider import ScheduleProvider
from bhamon_orchestra_model.user_provider import UserProvider
from bhamon_orchestra_model.worker_provider import WorkerProvider

import bhamon_orchestra_master

import bhamon_orchestra_configuration
from bhamon_orchestra_configuration.worker_selector import WorkerSelector

import environment
import master_configuration


logger = logging.getLogger("Master")


def main():
	arguments = parse_arguments()
	environment_instance = environment.load_environment()
	environment.configure_logging(environment_instance, arguments)

	with open(arguments.configuration, mode = "r", encoding = "utf-8") as configuration_file:
		configuration = json.load(configuration_file)

	environment.configure_log_file(environment_instance, configuration["orchestra_master_log_file_path"])

	with filelock.FileLock("master.lock", 5):
		logger.info("Job Orchestra %s", bhamon_orchestra_master.__version__)
		logger.info("Configuration %s", bhamon_orchestra_configuration.__version__)
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

	database_metadata = None
	if configuration["orchestra_database_uri"].startswith("postgresql://"):
		database_metadata = importlib.import_module("bhamon_orchestra_model.database.sql_database_model").metadata

	database_client_factory = environment.create_database_client_factory(
			configuration["orchestra_database_uri"], configuration["orchestra_database_authentication"], database_metadata)
	file_storage_instance = FileStorage(configuration["orchestra_file_storage_path"])
	date_time_provider_instance = DateTimeProvider()

	authentication_provider_instance = AuthenticationProvider(date_time_provider_instance)
	authorization_provider_instance = AuthorizationProvider()
	job_provider_instance = JobProvider(date_time_provider_instance)
	project_provider_instance = ProjectProvider(date_time_provider_instance)
	run_provider_instance = RunProvider(file_storage_instance, date_time_provider_instance)
	schedule_provider_instance = ScheduleProvider(date_time_provider_instance)
	user_provider_instance = UserProvider(date_time_provider_instance)
	worker_provider_instance = WorkerProvider(date_time_provider_instance)

	protocol_factory = functools.partial(
		WebSocketServerProtocol,
		database_client_factory = database_client_factory,
		user_provider = user_provider_instance,
		authentication_provider = authentication_provider_instance,
		authorization_provider = authorization_provider_instance,
	)

	supervisor_instance = Supervisor(
		host = configuration["orchestra_master_listen_address"],
		port = configuration["orchestra_master_listen_port"],
		protocol_factory = protocol_factory,
		database_client_factory = database_client_factory,
		worker_provider = worker_provider_instance,
		run_provider = run_provider_instance,
	)

	worker_selector_instance = WorkerSelector(
		database_client_factory = database_client_factory,
		worker_provider = worker_provider_instance,
		supervisor = supervisor_instance,
	)

	job_scheduler_instance = JobScheduler(
		database_client_factory = database_client_factory,
		job_provider = job_provider_instance,
		run_provider = run_provider_instance,
		schedule_provider = schedule_provider_instance,
		supervisor = supervisor_instance,
		worker_selector = worker_selector_instance,
		date_time_provider = date_time_provider_instance,
	)

	master_instance = Master(
		database_client_factory = database_client_factory,
		project_provider = project_provider_instance,
		job_provider = job_provider_instance,
		schedule_provider = schedule_provider_instance,
		worker_provider = worker_provider_instance,
		job_scheduler = job_scheduler_instance,
		supervisor = supervisor_instance,
	)

	master_instance.apply_configuration(master_configuration.configure(environment_instance))

	return master_instance


if __name__ == "__main__":
	main()
