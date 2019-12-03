import argparse
import getpass
import json
import logging
import os
import platform
import socket

import filelock

from bhamon_orchestra_worker.worker import Worker

import environment


def main():
	environment.configure_logging(logging.INFO)
	arguments = parse_arguments()
	executor_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "executor_main.py"))

	with open(arguments.configuration, "r") as configuration_file:
		configuration = json.load(configuration_file)

	worker_path = configuration["orchestra_workers"][arguments.identifier]["path"]
	worker_log_path = configuration["orchestra_workers"][arguments.identifier]["log"]
	os.makedirs(worker_path, exist_ok = True)

	os.chdir(worker_path)

	with filelock.FileLock("worker.lock", 5):
		environment.configure_log_file(worker_log_path, logging.INFO)
		worker_instance = create_application(arguments.identifier, configuration, executor_script)
		worker_instance.run()


def parse_arguments():
	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--identifier", required = True, metavar = "<identifier>", help = "set the identifier for this worker")
	argument_parser.add_argument("--configuration", default = "orchestra.json", metavar = "<path>", help = "set the configuration file path")
	return argument_parser.parse_args()


def create_application(local_worker_identifier, configuration, executor_script):
	worker_definition = configuration["orchestra_workers"][local_worker_identifier]
	worker_identifier = worker_definition["identifier"].format(host = socket.gethostname())

	write_local_configuration(configuration)
	authentication = load_authentication()
	properties = load_properties(worker_definition)

	return Worker(
		identifier = worker_identifier,
		master_uri = configuration["orchestra_master_url"],
		user = authentication["user"],
		secret = authentication["secret"],
		properties = properties,
		executor_script = executor_script,
	)


def write_local_configuration(global_configuration):
	configuration_file_path = "worker.json"

	local_configuration = {
		"orchestra_service_url": global_configuration["orchestra_service_url"],
		"authentication_file_path": os.path.abspath("authentication.json"),
		"artifact_server_url": global_configuration["artifact_server_url"],
		"artifact_server_parameters": global_configuration.get("artifact_server_parameters", {}),
		"artifact_server_web_url": global_configuration["artifact_server_web_url"],
		"python_package_repository_url": global_configuration["python_package_repository_url"],
		"python_package_repository_parameters": global_configuration.get("python_package_repository_parameters", {}),
		"python_package_repository_web_url": global_configuration["python_package_repository_web_url"],
	}

	with open(configuration_file_path, "w") as configuration_file:
		json.dump(local_configuration, configuration_file, indent = 4)


def load_authentication():
	authentication_file_path = "authentication.json"

	if os.path.exists(authentication_file_path):
		with open(authentication_file_path, "r") as authentication_file:
			return json.load(authentication_file)

	authentication = {
		"user": input("User: "),
		"secret": getpass.getpass("Secret: "),
	}

	with open(authentication_file_path, "w") as authentication_file:
		json.dump(authentication, authentication_file, indent = 4)

	return authentication


def load_properties(worker_definition):
	properties = {
		"host": socket.gethostname(),
		"operating_system": platform.system().lower(),
	}

	properties.update(worker_definition.get("properties", {}))

	return properties


if __name__ == "__main__":
	main()
