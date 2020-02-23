import argparse
import json
import logging
import types

from bhamon_orchestra_model.authentication_provider import AuthenticationProvider
from bhamon_orchestra_model.authorization_provider import AuthorizationProvider
from bhamon_orchestra_model.database.file_storage import FileStorage
from bhamon_orchestra_model.date_time_provider import DateTimeProvider
from bhamon_orchestra_model.job_provider import JobProvider
from bhamon_orchestra_model.run_provider import RunProvider
from bhamon_orchestra_model.task_provider import TaskProvider
from bhamon_orchestra_model.user_provider import UserProvider
from bhamon_orchestra_model.worker_provider import WorkerProvider

import bhamon_orchestra_cli.admin_controller as admin_controller
import bhamon_orchestra_cli.database_controller as database_controller

import environment


def main():
	environment.configure_logging(logging.INFO)
	arguments = parse_arguments()

	with open(arguments.configuration, "r") as configuration_file:
		configuration = json.load(configuration_file)

	application = create_application(configuration)
	result = arguments.handler(application, arguments)
	if result is not None:
		print(json.dumps(result, indent = 4))


def parse_arguments():
	main_parser = argparse.ArgumentParser()
	main_parser.add_argument("--configuration", default = "orchestra.json", metavar = "<path>", help = "set the configuration file path")

	subparsers = main_parser.add_subparsers(title = "commands", metavar = "<command>")
	subparsers.required = True

	admin_controller.register_commands(subparsers)
	database_controller.register_commands(subparsers)

	return main_parser.parse_args()


def create_application(configuration):
	database_client_instance = environment.create_database_client(configuration["orchestra_database_uri"], configuration["orchestra_database_authentication"])
	file_storage_instance = FileStorage(configuration["orchestra_file_storage_path"])
	date_time_provider_instance = DateTimeProvider()

	application = types.SimpleNamespace()
	application.database_uri = configuration["orchestra_database_uri"]
	application.database_authentication = configuration["orchestra_database_authentication"]

	application.authentication_provider = AuthenticationProvider(database_client_instance, date_time_provider_instance)
	application.authorization_provider = AuthorizationProvider()
	application.job_provider = JobProvider(database_client_instance, date_time_provider_instance)
	application.run_provider = RunProvider(database_client_instance, file_storage_instance, date_time_provider_instance)
	application.task_provider = TaskProvider(database_client_instance, date_time_provider_instance)
	application.user_provider = UserProvider(database_client_instance, date_time_provider_instance)
	application.worker_provider = WorkerProvider(database_client_instance, date_time_provider_instance)

	return application


if __name__ == "__main__":
	main()
