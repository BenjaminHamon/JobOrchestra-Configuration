import argparse
import importlib
import logging
import types

from bhamon_orchestra_model.database.file_data_storage import FileDataStorage
from bhamon_orchestra_model.date_time_provider import DateTimeProvider
from bhamon_orchestra_model.job_provider import JobProvider
from bhamon_orchestra_model.project_provider import ProjectProvider
from bhamon_orchestra_model.run_provider import RunProvider
from bhamon_orchestra_model.schedule_provider import ScheduleProvider
from bhamon_orchestra_model.serialization.json_serializer import JsonSerializer
from bhamon_orchestra_model.users.authentication_provider import AuthenticationProvider
from bhamon_orchestra_model.users.authorization_provider import AuthorizationProvider
from bhamon_orchestra_model.users.user_provider import UserProvider
from bhamon_orchestra_model.worker_provider import WorkerProvider

import bhamon_orchestra_cli
import bhamon_orchestra_cli.admin_controller as admin_controller
import bhamon_orchestra_cli.database_controller as database_controller

import environment
import factory


logger = logging.getLogger("Main")


def main():
	arguments = parse_arguments()
	environment_instance = environment.load_environment()
	environment.configure_logging(environment_instance, arguments)

	application_title = bhamon_orchestra_cli.__product__ + " " + "CLI"
	application_version = bhamon_orchestra_cli.__version__

	logger.info("%s %s", application_title, application_version)

	serializer = JsonSerializer(indent = 4)
	configuration = serializer.deserialize_from_file(arguments.configuration)
	application = create_application(configuration)

	result = arguments.handler(application, arguments)

	if result is not None:
		print(serializer.serialize_to_string(result))


def parse_arguments():
	main_parser = argparse.ArgumentParser()
	main_parser.add_argument("--configuration", default = "orchestra.json", metavar = "<path>", help = "set the configuration file path")

	subparsers = main_parser.add_subparsers(title = "commands", metavar = "<command>")
	subparsers.required = True

	admin_controller.register_commands(subparsers)
	database_controller.register_commands(subparsers)

	return main_parser.parse_args()


def create_application(configuration):
	database_metadata = None
	if configuration["orchestra_database_uri"].startswith("postgresql://"):
		database_metadata = importlib.import_module("bhamon_orchestra_model.database.sql_database_model").metadata

	database_administration_factory = factory.create_database_administration_factory(
		database_uri = configuration["orchestra_database_uri"],
		database_authentication = configuration["orchestra_database_authentication"],
		database_metadata = database_metadata,
	)

	database_client_factory = factory.create_database_client_factory(
		database_uri = configuration["orchestra_database_uri"],
		database_authentication = configuration["orchestra_database_authentication"],
		database_metadata = database_metadata,
	)

	data_storage_instance = FileDataStorage(configuration["orchestra_file_storage_path"])
	date_time_provider_instance = DateTimeProvider()

	application = types.SimpleNamespace()
	application.database_administration_factory = database_administration_factory
	application.database_client_factory = database_client_factory
	application.authentication_provider = AuthenticationProvider(date_time_provider_instance)
	application.authorization_provider = AuthorizationProvider()
	application.job_provider = JobProvider(date_time_provider_instance)
	application.project_provider = ProjectProvider(date_time_provider_instance)
	application.run_provider = RunProvider(data_storage_instance, date_time_provider_instance)
	application.schedule_provider = ScheduleProvider(date_time_provider_instance)
	application.user_provider = UserProvider(date_time_provider_instance)
	application.worker_provider = WorkerProvider(date_time_provider_instance)

	return application


if __name__ == "__main__":
	main()
