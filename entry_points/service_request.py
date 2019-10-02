import argparse
import json

import requests


def main():
	arguments = parse_arguments()
	with open(arguments.configuration, "r") as configuration_file:
		configuration = json.load(configuration_file)
	with open(arguments.authentication, "r") as authentication_file:
		authentication = json.load(authentication_file)

	response = send_request(
		method = arguments.method,
		service_url = configuration["build_service_url"],
		route = arguments.route,
		authentication = (authentication["user"], authentication["secret"]) if authentication else None,
		parameters = arguments.parameters,
	)

	if response:
		print(json.dumps(response, indent = 4))


def parse_arguments():

	def parse_key_value_parameter(argument_value):
		key_value = argument_value.split("=")
		if len(key_value) != 2:
			raise argparse.ArgumentTypeError("invalid key value parameter: '%s'" % argument_value)
		return (key_value[0], key_value[1])

	argument_parser = argparse.ArgumentParser()
	argument_parser.add_argument("--configuration", default = "build_service.json", metavar = "<path>", help = "set the configuration file path")
	argument_parser.add_argument("--authentication", default = "authentication.json", metavar = "<path>", help = "set the authentication file path")
	argument_parser.add_argument("--method", required = True, type = str.upper, choices = [ "GET", "POST" ], help = "set the web request method")
	argument_parser.add_argument("--route", required = True, metavar = "<route>", help = "set the web request route")
	argument_parser.add_argument("--parameters", nargs = "+", type = parse_key_value_parameter, default = [], metavar = "<key=value>", help = "set the web request parameters")

	arguments = argument_parser.parse_args()
	arguments.parameters = dict(arguments.parameters)

	return arguments


def send_request(method, service_url, route, authentication, parameters):
	if method == "GET":
		return get(service_url, route, authentication, parameters)
	if method == "POST":
		return post(service_url, route, authentication, parameters)
	raise ValueError("Unsupported method: '%s'" % method)


def get(service_url, route, authentication, parameters = None):
	headers = { "Content-Type": "application/json" }
	if parameters is None:
		parameters = {}

	response = requests.get(service_url + route, auth = authentication, headers = headers, params = parameters)
	response.raise_for_status()
	return response.json()


def post(service_url, route, authentication, data = None):
	headers = { "Content-Type": "application/json" }
	if data is None:
		data = {}

	response = requests.post(service_url + route, auth = authentication, headers = headers, data = json.dumps(data))
	response.raise_for_status()
	return response.json()


if __name__ == "__main__":
	main()
