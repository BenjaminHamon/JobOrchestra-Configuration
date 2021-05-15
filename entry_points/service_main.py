import argparse
import importlib
import logging

import flask

from bhamon_orchestra_model.database.file_data_storage import FileDataStorage
from bhamon_orchestra_model.date_time_provider import DateTimeProvider
from bhamon_orchestra_model.file_server_client import FileServerClient
from bhamon_orchestra_model.job_provider import JobProvider
from bhamon_orchestra_model.project_provider import ProjectProvider
from bhamon_orchestra_model.revision_control.github import GitHubClient
from bhamon_orchestra_model.run_provider import RunProvider
from bhamon_orchestra_model.schedule_provider import ScheduleProvider
from bhamon_orchestra_model.serialization.json_serializer import JsonSerializer
from bhamon_orchestra_model.users.authentication_provider import AuthenticationProvider
from bhamon_orchestra_model.users.authorization_provider import AuthorizationProvider
from bhamon_orchestra_model.users.user_provider import UserProvider
from bhamon_orchestra_model.worker_provider import WorkerProvider

import bhamon_orchestra_service
import bhamon_orchestra_service.service_setup as service_setup
from bhamon_orchestra_service.admin_controller import AdminController
from bhamon_orchestra_service.job_controller import JobController
from bhamon_orchestra_service.me_controller import MeController
from bhamon_orchestra_service.project_controller import ProjectController
from bhamon_orchestra_service.response_builder import ResponseBuilder
from bhamon_orchestra_service.run_controller import RunController
from bhamon_orchestra_service.schedule_controller import ScheduleController
from bhamon_orchestra_service.service import Service
from bhamon_orchestra_service.user_controller import UserController
from bhamon_orchestra_service.worker_controller import WorkerController

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

	serializer_instance = JsonSerializer()
	configuration = serializer_instance.deserialize_from_file(arguments.configuration)

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


def create_application(configuration): # pylint: disable = too-many-locals
	application = flask.Flask(__name__)

	external_services = {
		"artifacts": FileServerClient("Artifact Server", configuration["artifact_server_web_url"]),
		"github": GitHubClient(configuration.get("github_access_token", None)),
		"python_packages": FileServerClient("Python Package Repository", configuration["python_package_repository_web_url"]),
	}

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
	serializer_instance = JsonSerializer()
	response_builder_instance = ResponseBuilder(application, serializer_instance)

	authentication_provider_instance = AuthenticationProvider(date_time_provider_instance)
	authorization_provider_instance = AuthorizationProvider()
	job_provider_instance = JobProvider(date_time_provider_instance)
	project_provider_instance = ProjectProvider(date_time_provider_instance)
	run_provider_instance = RunProvider(data_storage_instance, date_time_provider_instance)
	schedule_provider_instance = ScheduleProvider(date_time_provider_instance)
	user_provider_instance = UserProvider(date_time_provider_instance)
	worker_provider_instance = WorkerProvider(date_time_provider_instance)

	service_instance = Service(
		application = application,
		response_builder = response_builder_instance,
		database_client_factory = database_client_factory,
		authentication_provider = authentication_provider_instance,
		authorization_provider = authorization_provider_instance,
		user_provider = user_provider_instance,
	)

	run_controller_serializer = JsonSerializer(indent = 4)

	admin_controller_instance = AdminController(response_builder_instance, external_services)
	job_controller_instance = JobController(response_builder_instance, job_provider_instance, run_provider_instance)
	project_controller_instance = ProjectController(application, response_builder_instance, project_provider_instance, run_provider_instance)
	run_controller_instance = RunController(response_builder_instance, run_controller_serializer, run_provider_instance)
	schedule_controller_instance = ScheduleController(response_builder_instance, schedule_provider_instance)
	user_controller_instance = UserController(response_builder_instance, authentication_provider_instance, user_provider_instance)
	worker_controller_instance = WorkerController(response_builder_instance, job_provider_instance, run_provider_instance, worker_provider_instance)
	me_controller_instance = MeController(response_builder_instance, authentication_provider_instance, user_provider_instance, user_controller_instance)

	service_setup.configure(application)
	service_setup.register_handlers(application, service_instance)

	service_setup.register_routes(
		application = application,
		service = service_instance,
		admin_controller = admin_controller_instance,
		job_controller = job_controller_instance,
		me_controller = me_controller_instance,
		project_controller = project_controller_instance,
		run_controller = run_controller_instance,
		schedule_controller = schedule_controller_instance,
		user_controller = user_controller_instance,
		worker_controller = worker_controller_instance,
	)

	application.config["GITHUB_ACCESS_TOKEN"] = configuration.get("github_access_token", None)

	return application


def transform_run_results(project_identifier, run_identifier, run_results): # pylint: disable = unused-argument
	database_client = flask.request.database_client()
	project = flask.current_app.project_provider.get(database_client, project_identifier)
	return run_result_transformer.transform_run_results(project, run_results)


if __name__ == "__main__":
	main()
