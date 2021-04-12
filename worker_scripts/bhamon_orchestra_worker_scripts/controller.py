import argparse
import logging

from bhamon_orchestra_model.serialization.json_serializer import JsonSerializer
from bhamon_orchestra_worker.controller import Controller
from bhamon_orchestra_worker.web_service_client import WebServiceClient

import bhamon_orchestra_worker_scripts.environment as environment


logger = logging.getLogger("Main")


def main():
	arguments = parse_arguments()
	environment_instance = environment.load_environment()
	environment.configure_logging(environment_instance, None)

	serializer_instance = JsonSerializer()
	configuration = serializer_instance.deserialize_from_file(arguments.configuration)
	authentication = serializer_instance.deserialize_from_file(configuration["authentication_file_path"])
	service_authorization = (authentication["user"], authentication["secret"])
	service_client_instance = WebServiceClient(serializer_instance, configuration["orchestra_service_url"], authorization = service_authorization)
	controller_instance = Controller(service_client_instance, None, arguments.results)

	controller_instance.reload()

	if arguments.command == "trigger":
		controller_instance.trigger_source = { "type": "run", "project": arguments.source_project, "identifier": arguments.source_run }
		controller_instance.trigger(arguments.project, arguments.job, arguments.parameters)
	if arguments.command == "wait":
		controller_instance.wait()


def parse_arguments():

	def parse_key_value_parameter(argument_value):
		key_value = argument_value.split("=")
		if len(key_value) != 2:
			raise argparse.ArgumentTypeError("invalid key value parameter: '%s'" % argument_value)
		return (key_value[0], key_value[1])

	main_parser = argparse.ArgumentParser()
	main_parser.add_argument("--configuration", required = True, metavar = "<path>", help = "set the worker configuration file path")
	main_parser.add_argument("--results", required = True, metavar = "<path>", help = "set the file path where to store the run results")

	subparsers = main_parser.add_subparsers(title = "commands", dest = "command", metavar = "<command>")
	subparsers.required = True

	command_parser = subparsers.add_parser("trigger", help = "trigger a run")
	command_parser.add_argument("--project", required = True, help = "set the project to trigger a run for")
	command_parser.add_argument("--job", required = True, help = "set the job to trigger a run for")
	command_parser.add_argument("--source-project", required = True, help = "set the project serving as the trigger source")
	command_parser.add_argument("--source-run", required = True, help = "set the run serving as the trigger source")
	command_parser.add_argument("--parameters", nargs = "*", type = parse_key_value_parameter, default = [],
		metavar = "<key=value>", help = "set parameters for the artifact")

	command_parser = subparsers.add_parser("wait", help = "wait for triggered runs")

	arguments = main_parser.parse_args()
	if hasattr(arguments, "parameters"):
		arguments.parameters = dict(arguments.parameters)

	return arguments


if __name__ == "__main__":
	main()
