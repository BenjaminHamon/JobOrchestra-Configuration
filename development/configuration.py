import datetime
import subprocess

import development.commands.clean
import development.commands.develop
import development.commands.lint


def get_command_list():
	return [
		development.commands.clean,
		development.commands.develop,
		development.commands.lint,
	]


def load_configuration(environment):
	configuration = {
		"project": "bhamon-build-configuration",
		"project_name": "Build Service Configuration",
		"project_version": { "identifier": "1.0" },
	}

	branch = subprocess.check_output([ environment["git_executable"], "rev-parse", "--abbrev-ref", "HEAD" ]).decode("utf-8").strip()
	revision = subprocess.check_output([ environment["git_executable"], "rev-parse", "--short=10", "HEAD" ]).decode("utf-8").strip()
	revision_date = int(subprocess.check_output([ environment["git_executable"], "show", "--no-patch", "--format=%ct", revision ]).decode("utf-8").strip())
	revision_date = datetime.datetime.utcfromtimestamp(revision_date).replace(microsecond = 0).isoformat() + "Z"

	configuration["project_version"]["branch"] = branch
	configuration["project_version"]["revision"] = revision
	configuration["project_version"]["date"] = revision_date
	configuration["project_version"]["numeric"] = "{identifier}".format(**configuration["project_version"])
	configuration["project_version"]["full"] = "{identifier}+{revision}".format(**configuration["project_version"])

	configuration["author"] = "Benjamin Hamon"
	configuration["author_email"] = "hamon.benjamin@gmail.com"
	configuration["project_url"] = "https://github.com/BenjaminHamon/BuildService"
	configuration["copyright"] = "Copyright © 2019 Benjamin Hamon"

	configuration["development_dependencies"] = [ "pylint", "pymongo" ]

	configuration["components"] = [
		{ "name": "bhamon-build-configuration", "path": "master_configuration", "packages": [ "bhamon_build_configuration" ] },
		{ "name": "bhamon-build-model-extensions", "path": "model_extensions", "packages": [ "bhamon_build_model_extensions" ] },
		{ "name": "bhamon-build-service-extensions", "path": "service_extensions", "packages": [ "bhamon_build_service_extensions" ] },
		{ "name": "bhamon-build-website-extensions", "path": "website_extensions", "packages": [ "bhamon_build_website_extensions" ] },
		{ "name": "bhamon-build-worker-extensions", "path": "worker_extensions", "packages": [ "bhamon_build_worker_extensions" ] },
	]

	return configuration


def get_setuptools_parameters(configuration):
	return {
		"version": configuration["project_version"]["full"],
		"author": configuration["author"],
		"author_email": configuration["author_email"],
		"url": configuration["project_url"],
	}
