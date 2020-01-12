repository = "https://github.com/BenjaminHamon/BuildService"

initialization_script = "bhamon_orchestra_worker_scripts.build_service"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_services(environment):
	return {
		"artifact_repository": {
			"url": environment["artifact_server_url"] + "/" + "BuildService",
			"file_types": {
				"package": { "path_in_repository": "packages", "file_extension": ".zip" },
			},
		},

		"python_package_repository": {
			"url": environment["python_package_repository_url"],
			"distribution_extension": "-py3-none-any.whl",
		},

		"revision_control": {
			"type": "github",
			"repository": "BenjaminHamon/BuildService",
		}
	}


def configure_jobs():
	return [
		check("linux"),
		check("windows"),
		package(),
		distribute(),
	]


def check(platform):
	job = {
		"identifier": "build-service_check_" + platform,
		"description": "Run checks for the BuildService project.",
		"project": "build-service",
		"workspace": "build-service",

		"properties": {
			"operating_system": [ platform ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters},
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "develop", "command": project_entry_point + [ "develop" ] },
		{ "name": "lint", "command": project_entry_point + [ "lint" ] },
		{ "name": "test", "command": project_entry_point + [ "test" ] },
	]

	return job


def package():
	job = {
		"identifier": "build-service_package",
		"description": "Generate distribution packages for the BuildService project.",
		"project": "build-service",
		"workspace": "build-service",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters},
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "develop", "command": project_entry_point + [ "develop" ] },
		{ "name": "lint", "command": project_entry_point + [ "lint" ] },
		{ "name": "test", "command": project_entry_point + [ "test" ] },
		{ "name": "distribute package", "command": project_entry_point + [ "distribute", "package" ] },
		{ "name": "artifact package", "command": project_entry_point + [ "artifact", "package", "package" ] },
		{ "name": "artifact verify", "command": project_entry_point + [ "artifact", "verify", "package" ] },
		{ "name": "artifact upload", "command": project_entry_point + [ "artifact", "upload", "package" ] },
	]

	return job


def distribute():
	job = {
		"identifier": "build-service_distribute",
		"description": "Upload distribution packages for the BuildService project to the python package repository.",
		"project": "build-service",
		"workspace": "build-service",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters},
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "develop", "command": project_entry_point + [ "develop" ] },
		{ "name": "artifact download", "command": project_entry_point + [ "artifact", "download", "package" ] },
		{ "name": "artifact install", "command": project_entry_point + [ "artifact", "install", "package" ] },
		{ "name": "distribute upload", "command": project_entry_point + [ "distribute", "upload" ] },
	]

	return job