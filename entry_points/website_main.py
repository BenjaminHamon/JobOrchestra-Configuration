import argparse
import json
import logging
import os

import flask

from bhamon_orchestra_model.authorization_provider import AuthorizationProvider
from bhamon_orchestra_model.date_time_provider import DateTimeProvider

import bhamon_orchestra_website
import bhamon_orchestra_website.website as website

import bhamon_orchestra_configuration
import bhamon_orchestra_configuration.website_extensions as website_extensions

import environment


logger = logging.getLogger("Website")


def main():
	environment.configure_logging(logging.INFO)
	arguments = parse_arguments()

	with open(arguments.configuration, "r") as configuration_file:
		configuration = json.load(configuration_file)
	environment.configure_log_file(configuration["orchestra_website_log_file_path"], logging.INFO)

	development_options = {
		"debug": True,
		"host": configuration["orchestra_website_listen_address"],
		"port": configuration["orchestra_website_listen_port"],
	}

	logger.info("Job Orchestra %s", bhamon_orchestra_website.__version__)
	application = create_application(configuration)
	application.config["WEBSITE_ANNOUNCEMENT"] = "Development Environment"
	application.config["WEBSITE_ANNOUNCEMENT_TYPE"] = "warning"
	application.run(**development_options)


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--configuration", default = "orchestra.json", metavar = "<path>", help = "set the configuration file path")
	return argument_parser.parse_args()


def create_application(configuration):
	application = flask.Flask(__name__, static_folder = None)
	application.authorization_provider = AuthorizationProvider()
	application.date_time_provider = DateTimeProvider()
	application.artifact_server_url = configuration["artifact_server_web_url"]
	application.python_package_repository_url = configuration["python_package_repository_web_url"]
	application.service_url = configuration["orchestra_service_url"]
	application.secret_key = configuration["orchestra_website_secret"]

	resource_paths = [
		os.path.dirname(bhamon_orchestra_configuration.__file__),
		os.path.dirname(bhamon_orchestra_website.__file__),
	]

	website.configure(application)
	website.register_handlers(application)
	website.register_resources(application, resource_paths)
	website.register_routes(application)
	website_extensions.register_routes(application)

	return application


if __name__ == "__main__":
	main()
