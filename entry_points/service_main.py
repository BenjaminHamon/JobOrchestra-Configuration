import argparse
import importlib
import json
import logging

import flask

from bhamon_orchestra_model.authentication_provider import AuthenticationProvider
from bhamon_orchestra_model.authorization_provider import AuthorizationProvider
from bhamon_orchestra_model.database.file_data_storage import FileDataStorage
from bhamon_orchestra_model.date_time_provider import DateTimeProvider
from bhamon_orchestra_model.file_server_client import FileServerClient
from bhamon_orchestra_model.job_provider import JobProvider
from bhamon_orchestra_model.project_provider import ProjectProvider
from bhamon_orchestra_model.revision_control.github import GitHubClient
from bhamon_orchestra_model.run_provider import RunProvider
from bhamon_orchestra_model.schedule_provider import ScheduleProvider
from bhamon_orchestra_model.user_provider import UserProvider
from bhamon_orchestra_model.worker_provider import WorkerProvider

import bhamon_orchestra_service
import bhamon_orchestra_service.service as service

import bhamon_orchestra_configuration.run_result_transformer as run_result_transformer

import environment
import factory


logger = logging.getLogger("Main")


def main():
	arguments = parse_arguments()
	environment_instance = environment.load_environment()
	environment.configure_logging(environment_instance, arguments)

	application_title = bhamon_orchestra_service.__product__ + " " + "Service"
	application_version = bhamon_orchestra_service.__version__

	with open(arguments.configuration, mode = "r", encoding = "utf-8") as configuration_file:
		configuration = json.load(configuration_file)

	environment.configure_log_file(environment_instance, configuration["orchestra_service_log_file_path"])

	development_options = {
		"debug": True,
		"host": configuration["orchestra_service_listen_address"],
		"port": configuration["orchestra_service_listen_port"],
	}

	logging.getLogger("Application").info("%s %s", application_title, application_version)

	application = create_application(configuration)
	application.run(**development_options)


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--configuration", default = "orchestra.json", metavar = "<path>", help = "set the configuration file path")
	return argument_parser.parse_args()


def create_application(configuration):
	database_metadata = None
	if configuration["orchestra_database_uri"].startswith("postgresql://"):
		database_metadata = importlib.import_module("bhamon_orchestra_model.database.sql_database_model").metadata

	database_client_factory = factory.create_database_client_factory(
		database_uri = configuration["orchestra_database_uri"],
		database_authentication = configuration["orchestra_database_authentication"],
		database_metadata = database_metadata,
	)

	data_storage_instance = FileDataStorage(configuration["orchestra_file_storage_path"])
	date_time_provider_instance = DateTimeProvider()

	application = flask.Flask(__name__)
	application.database_client_factory = database_client_factory
	application.authentication_provider = AuthenticationProvider(date_time_provider_instance)
	application.authorization_provider = AuthorizationProvider()
	application.job_provider = JobProvider(date_time_provider_instance)
	application.project_provider = ProjectProvider(date_time_provider_instance)
	application.run_provider = RunProvider(data_storage_instance, date_time_provider_instance)
	application.schedule_provider = ScheduleProvider(date_time_provider_instance)
	application.user_provider = UserProvider(date_time_provider_instance)
	application.worker_provider = WorkerProvider(date_time_provider_instance)

	application.run_result_transformer = transform_run_results

	service.configure(application)
	service.register_handlers(application)
	service.register_routes(application)

	application.external_services = {
		"artifacts": FileServerClient("Artifact Server", configuration["artifact_server_web_url"]),
		"github": GitHubClient(configuration.get("github_access_token", None)),
		"python_packages": FileServerClient("Python Package Repository", configuration["python_package_repository_web_url"]),
	}

	application.config["GITHUB_ACCESS_TOKEN"] = configuration.get("github_access_token", None)

	return application


def transform_run_results(project_identifier, run_identifier, run_results): # pylint: disable = unused-argument
	database_client = flask.request.database_client()
	project = flask.current_app.project_provider.get(database_client, project_identifier)
	return run_result_transformer.transform_run_results(project, run_results)


if __name__ == "__main__":
	main()
