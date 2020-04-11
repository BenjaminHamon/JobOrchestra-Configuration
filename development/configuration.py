import datetime
import glob
import importlib
import os
import subprocess
import sys


def load_configuration(environment):
	configuration = {
		"project": "bhamon-orchestra-configuration",
		"project_name": "Job Orchestra Configuration",
		"project_version": load_project_version(environment["git_executable"], "2.0"),
	}

	configuration["author"] = "Benjamin Hamon"
	configuration["author_email"] = "hamon.benjamin@gmail.com"
	configuration["project_url"] = "https://github.com/BenjaminHamon/JobOrchestra"
	configuration["copyright"] = "Copyright (c) 2020 Benjamin Hamon"

	configuration["development_toolkit"] = "git+https://github.com/BenjaminHamon/DevelopmentToolkit@{revision}#subdirectory=toolkit"
	configuration["development_toolkit_revision"] = "5e12ab4651373b0399201075ea9e78cb0015b091"
	configuration["development_dependencies"] = [ "pylint", "pymongo", "wheel" ]

	configuration["project_dependencies"] = [
		"bhamon-orchestra-cli ~= 2.0",
		"bhamon-orchestra-model ~= 2.0",
		"bhamon-orchestra-master ~= 2.0",
		"bhamon-orchestra-service ~= 2.0",
		"bhamon-orchestra-website ~= 2.0",
		"bhamon-orchestra-worker ~= 2.0",
	]

	configuration["components"] = [
		{ "name": "bhamon-orchestra-configuration", "path": "master_configuration" },
		{ "name": "bhamon-orchestra-worker-scripts", "path": "worker_scripts" },
	]

	configuration["project_identifier_for_artifact_server"] = "JobOrchestra-Configuration"

	configuration["artifact_directory"] = "artifacts"

	configuration["filesets"] = load_filesets(configuration)
	configuration["artifacts"] = load_artifacts(configuration)

	return configuration


def load_project_version(git_executable, identifier):
	branch = subprocess.check_output([ git_executable, "rev-parse", "--abbrev-ref", "HEAD" ], universal_newlines = True).strip()
	revision = subprocess.check_output([ git_executable, "rev-parse", "--short=10", "HEAD" ], universal_newlines = True).strip()
	revision_date = int(subprocess.check_output([ git_executable, "show", "--no-patch", "--format=%ct", revision ], universal_newlines = True).strip())
	revision_date = datetime.datetime.utcfromtimestamp(revision_date).replace(microsecond = 0).isoformat() + "Z"

	return {
		"identifier": identifier,
		"numeric": identifier,
		"full": identifier + "+" + revision,
		"branch": branch,
		"revision": revision,
		"date": revision_date,
	}


def load_filesets(configuration):
	return {
		"distribution": {
			"path_in_workspace": os.path.join(configuration["artifact_directory"], "distributions", "{component}"),
			"file_functions": [ _list_distribution_files ],
		},
	}


def load_artifacts(configuration):
	return {
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


def get_setuptools_parameters(configuration):
	return {
		"version": configuration["project_version"]["full"],
		"author": configuration["author"],
		"author_email": configuration["author_email"],
		"url": configuration["project_url"],
	}


def list_package_data(package, pattern_collection):
	all_files = []
	for pattern in pattern_collection:
		all_files += glob.glob(package + "/" + pattern, recursive = True)
	return [ os.path.relpath(path, package) for path in all_files ]


def load_commands():
	all_modules = [
		"development.commands.artifact",
		"development.commands.clean",
		"development.commands.develop",
		"development.commands.distribute",
		"development.commands.info",
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
