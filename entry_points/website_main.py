import argparse
import logging
import os

import flask

from bhamon_orchestra_model.authorization_provider import AuthorizationProvider
from bhamon_orchestra_model.date_time_provider import DateTimeProvider
from bhamon_orchestra_model.serialization.json_serializer import JsonSerializer

import bhamon_orchestra_website
import bhamon_orchestra_website.website_setup as website_setup
from bhamon_orchestra_website.admin_controller import AdminController
from bhamon_orchestra_website.job_controller import JobController
from bhamon_orchestra_website.me_controller import MeController
from bhamon_orchestra_website.project_controller import ProjectController
from bhamon_orchestra_website.run_controller import RunController
from bhamon_orchestra_website.schedule_controller import ScheduleController
from bhamon_orchestra_website.service_client import ServiceClient
from bhamon_orchestra_website.user_controller import UserController
from bhamon_orchestra_website.website import Website
from bhamon_orchestra_website.worker_controller import WorkerController

import bhamon_orchestra_configuration
import bhamon_orchestra_configuration.website_extensions as website_extensions

import environment


logger = logging.getLogger("Main")


def main():
	arguments = parse_arguments()
	environment_instance = environment.load_environment()
	environment.configure_logging(environment_instance, arguments)

	application_title = bhamon_orchestra_website.__product__ + " " + "Website"
	application_version = bhamon_orchestra_website.__version__

	serializer_instance = JsonSerializer()
	configuration = serializer_instance.deserialize_from_file(arguments.configuration)

	environment.configure_log_file(environment_instance, configuration["orchestra_website_log_file_path"])

	development_options = {
		"debug": True,
		"host": configuration["orchestra_website_listen_address"],
		"port": configuration["orchestra_website_listen_port"],
	}

	logging.getLogger("Application").info("%s %s", application_title, application_version)

	application = create_application(configuration)
	application.config["WEBSITE_ANNOUNCEMENT"] = "Development Environment"
	application.config["WEBSITE_ANNOUNCEMENT_TYPE"] = "warning"
	application.run(**development_options)


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--configuration", default = "orchestra.json", metavar = "<path>", help = "set the configuration file path")
	return argument_parser.parse_args()


def create_application(configuration): # pylint: disable = too-many-locals
	application = flask.Flask(__name__, static_folder = None)
	application.artifact_server_url = configuration["artifact_server_web_url"]
	application.python_package_repository_url = configuration["python_package_repository_web_url"]
	application.secret_key = configuration["orchestra_website_secret"]

	resource_paths = [
		os.path.dirname(bhamon_orchestra_configuration.__file__),
		os.path.dirname(bhamon_orchestra_website.__file__),
	]

	date_time_provider_instance = DateTimeProvider()
	serializer_instance = JsonSerializer()
	authorization_provider_instance = AuthorizationProvider()
	service_client_instance = ServiceClient(serializer_instance, configuration["orchestra_service_url"])

	website_instance = Website(application, date_time_provider_instance, authorization_provider_instance, service_client_instance)
	admin_controller_instance = AdminController(application, service_client_instance)
	job_controller_instance = JobController(service_client_instance)
	me_controller_instance = MeController(date_time_provider_instance, service_client_instance)
	project_controller_instance = ProjectController(service_client_instance)
	run_controller_instance = RunController(service_client_instance)
	schedule_controller_instance = ScheduleController(service_client_instance)
	user_controller_instance = UserController(date_time_provider_instance, authorization_provider_instance, service_client_instance)
	worker_controller_instance = WorkerController(service_client_instance)

	website_setup.configure(application, website_instance)
	website_setup.register_handlers(application, website_instance)
	website_setup.register_resources(application, resource_paths)

	website_setup.register_routes(
		application = application,
		website = website_instance,
		admin_controller = admin_controller_instance,
		job_controller = job_controller_instance,
		me_controller = me_controller_instance,
		project_controller = project_controller_instance,
		run_controller = run_controller_instance,
		schedule_controller = schedule_controller_instance,
		user_controller = user_controller_instance,
		worker_controller = worker_controller_instance,
	)

	website_extensions.register_routes(application)

	return application


if __name__ == "__main__":
	main()
