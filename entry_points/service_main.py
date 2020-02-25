import argparse
import json
import logging

import flask

from bhamon_orchestra_model.authentication_provider import AuthenticationProvider
from bhamon_orchestra_model.authorization_provider import AuthorizationProvider
from bhamon_orchestra_model.database.file_storage import FileStorage
from bhamon_orchestra_model.date_time_provider import DateTimeProvider
from bhamon_orchestra_model.file_server_client import FileServerClient
from bhamon_orchestra_model.job_provider import JobProvider
from bhamon_orchestra_model.project_provider import ProjectProvider
from bhamon_orchestra_model.revision_control.github import GitHubClient
from bhamon_orchestra_model.run_provider import RunProvider
from bhamon_orchestra_model.schedule_provider import ScheduleProvider
from bhamon_orchestra_model.task_provider import TaskProvider
from bhamon_orchestra_model.user_provider import UserProvider
from bhamon_orchestra_model.worker_provider import WorkerProvider

import bhamon_orchestra_service
import bhamon_orchestra_service.service as service

import bhamon_orchestra_configuration.run_result_transformer as run_result_transformer

import environment


logger = logging.getLogger("Service")


def main():
	environment.configure_logging(logging.INFO)
	arguments = parse_arguments()

	with open(arguments.configuration, "r") as configuration_file:
		configuration = json.load(configuration_file)
	environment.configure_log_file(configuration["orchestra_service_log_file_path"], logging.INFO)

	development_options = {
		"debug": True,
		"host": configuration["orchestra_service_listen_address"],
		"port": configuration["orchestra_service_listen_port"],
	}

	logger.info("Job Orchestra %s", bhamon_orchestra_service.__version__)
	application = create_application(configuration)
	application.run(**development_options)


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--configuration", default = "orchestra.json", metavar = "<path>", help = "set the configuration file path")
	return argument_parser.parse_args()


def create_application(configuration):
	database_client_instance = environment.create_database_client(configuration["orchestra_database_uri"], configuration["orchestra_database_authentication"])
	file_storage_instance = FileStorage(configuration["orchestra_file_storage_path"])
	date_time_provider_instance = DateTimeProvider()

	application = flask.Flask(__name__)
	application.authentication_provider = AuthenticationProvider(database_client_instance, date_time_provider_instance)
	application.authorization_provider = AuthorizationProvider()
	application.job_provider = JobProvider(database_client_instance, date_time_provider_instance)
	application.project_provider = ProjectProvider(database_client_instance, date_time_provider_instance)
	application.run_provider = RunProvider(database_client_instance, file_storage_instance, date_time_provider_instance)
	application.schedule_provider = ScheduleProvider(database_client_instance, date_time_provider_instance)
	application.task_provider = TaskProvider(database_client_instance, date_time_provider_instance)
	application.user_provider = UserProvider(database_client_instance, date_time_provider_instance)
	application.worker_provider = WorkerProvider(database_client_instance, date_time_provider_instance)

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
	project = flask.current_app.project_provider.get(project_identifier)
	return run_result_transformer.transform_run_results(project, run_results)


if __name__ == "__main__":
	main()
