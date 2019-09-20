import datetime
import importlib
import os
import subprocess
import sys


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
	configuration["copyright"] = "Copyright (c) 2019 Benjamin Hamon"

	configuration["development_toolkit"] = "git+https://github.com/BenjaminHamon/DevelopmentToolkit@{revision}#subdirectory=toolkit"
	configuration["development_toolkit_revision"] = "b1c386f93914950249b478a476bcb5347cfa0143"
	configuration["development_dependencies"] = [ "pylint", "pymongo", "wheel" ]

	configuration["components"] = [
		{ "name": "bhamon-build-configuration", "path": "master_configuration", "packages": [ "bhamon_build_configuration" ] },
		{ "name": "bhamon-build-model-extensions", "path": "model_extensions", "packages": [ "bhamon_build_model_extensions" ] },
		{ "name": "bhamon-build-service-extensions", "path": "service_extensions", "packages": [ "bhamon_build_service_extensions" ] },
		{ "name": "bhamon-build-website-extensions", "path": "website_extensions", "packages": [ "bhamon_build_website_extensions" ] },
		{ "name": "bhamon-build-worker-extensions", "path": "worker_extensions", "packages": [ "bhamon_build_worker_extensions" ] },
	]

	configuration["project_identifier_for_artifact_server"] = "BuildService-Configuration"

	configuration["filesets"] = {
		"distribution": {
			"path_in_workspace": os.path.join(".artifacts", "distributions", "{component}"),
			"file_functions": [ _list_distribution_files ],
		},
	}

	configuration["artifacts"] = {
		"package": {
			"file_name": "{project}_{version}_package",
			"installation_directory": ".artifacts/distributions",
			"path_in_repository": "packages",

			"filesets": [
				{
					"identifier": "distribution",
					"path_in_archive": component["name"],
					"parameters": {
						"component": component["name"],
					},
				}

				for component in configuration["components"]
			],
		},
	}

	return configuration


def get_setuptools_parameters(configuration):
	return {
		"version": configuration["project_version"]["full"],
		"author": configuration["author"],
		"author_email": configuration["author_email"],
		"url": configuration["project_url"],
	}


def load_commands():
	all_modules = [
		"development.commands.artifact",
		"development.commands.clean",
		"development.commands.develop",
		"development.commands.distribute",
		"development.commands.lint",
	]

	return [ import_command(module) for module in all_modules ]


def import_command(module_name):
	try:
		return {
			"module_name": module_name,
			"module": importlib.import_module(module_name),
		}

	except ImportError:
		return {
			"module_name": module_name,
			"exception": sys.exc_info(),
		}


def _list_distribution_files(path_in_workspace, parameters):
	archive_name = "{component}-{version}-py3-none-any.whl"
	archive_name = archive_name.format(component = parameters["component"].replace("-", "_"), version = parameters["version"])
	return [ os.path.join(path_in_workspace, archive_name) ]
