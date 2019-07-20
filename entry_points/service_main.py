import argparse
import json
import logging
import os

import flask

from bhamon_build_model.authentication_provider import AuthenticationProvider
from bhamon_build_model.authorization_provider import AuthorizationProvider
from bhamon_build_model.build_provider import BuildProvider
from bhamon_build_model.file_storage import FileStorage
from bhamon_build_model.job_provider import JobProvider
from bhamon_build_model.task_provider import TaskProvider
from bhamon_build_model.user_provider import UserProvider
from bhamon_build_model.worker_provider import WorkerProvider

import bhamon_build_service.service as service
import bhamon_build_service_extensions.service as service_extensions

import environment
import master_configuration


def main():
	environment.configure_logging(logging.INFO)
	arguments = parse_arguments()

	with open(arguments.configuration, "r") as configuration_file:
		configuration = json.load(configuration_file)

	development_options = {
		"debug": True,
		"host": configuration["build_service_listen_address"],
		"port": configuration["build_service_listen_port"],
	}

	application = create_application(configuration)
	application.run(**development_options)


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--configuration", default = "build_service.json", help = "set the configuration file path")
	return argument_parser.parse_args()


def create_application(configuration):
	database_client_instance = environment.create_database_client(configuration["build_database_uri"])
	file_storage_instance = FileStorage(configuration["build_file_storage_path"])

	application = flask.Flask(__name__)
	application.authentication_provider = AuthenticationProvider(database_client_instance)
	application.authorization_provider = AuthorizationProvider()
	application.build_provider = BuildProvider(database_client_instance, file_storage_instance)
	application.job_provider = JobProvider(database_client_instance)
	application.task_provider = TaskProvider(database_client_instance)
	application.user_provider = UserProvider(database_client_instance)
	application.worker_provider = WorkerProvider(database_client_instance)

	application.project_collection = master_configuration.configure_projects()

	service.register_handlers(application)
	service.register_routes(application)
	service_extensions.register_routes(application)

	return application


if __name__ == "__main__":
	main()
