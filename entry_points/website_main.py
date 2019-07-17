import argparse
import logging
import os

import flask

import bhamon_build_model.authorization_provider as authorization_provider

import bhamon_build_website
import bhamon_build_website.website as website

import bhamon_build_website_extensions
import bhamon_build_website_extensions.website as website_extensions

import environment


def main():
	environment.configure_logging(logging.INFO)
	environment_instance = environment.load_environment()
	arguments = parse_arguments()

	application = flask.Flask(__name__, static_folder = None)
	application.authorization_provider = authorization_provider.AuthorizationProvider()
	application.service_url = environment_instance["build_service_url"]
	application.artifact_storage_path = os.path.normpath(environment_instance["artifact_storage_path"])
	application.artifact_storage_url = environment_instance["artifact_storage_url"]

	with open(arguments.secret_path) as key_file:
		application.secret_key = key_file.read().strip()

	resource_paths = [
		os.path.dirname(bhamon_build_website_extensions.__file__),
		os.path.dirname(bhamon_build_website.__file__),
	]

	website.configure(application)
	website.register_handlers(application)
	website.register_resources(application, resource_paths)
	website.register_routes(application)
	website_extensions.register_routes(application)

	application.run(host = arguments.address, port = arguments.port, debug = True)


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--address", required = True, help = "set the address for the server to listen to")
	argument_parser.add_argument("--port", required = True, type = int, help = "set the port for the server to listen to")
	argument_parser.add_argument("--secret-path", required = True, metavar = "<path>", help = "set the path for a file containing the application secret")
	return argument_parser.parse_args()


if __name__ == "__main__":
	main()
