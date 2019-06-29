repository = "https://github.com/BenjaminHamon/BuildService"


def configure_services():
	return {
		"revision_control": {
			"service": "github",
			"parameters": {
				"owner": "BenjaminHamon",
				"repository": "BuildService",
			},
		}
	}


def configure_jobs():
	return [
		check("linux"),
		check("windows"),
		distribute(),
	]


def check(platform):
	job = {
		"identifier": "build-service_check_" + platform,
		"description": "Run checks for the BuildService project.",
		"workspace": "build-service",

		"properties": {
			"project": "build-service",
			"operating_system": [ platform ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_script = [ "{environment[python3_executable]}", "-u", "{environment[script_root]}/build_service.py", "--results", "{result_file_path}" ]
	project_script = [ ".venv/scripts/python", "-u", "scripts/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_script + [ "--repository", repository, "--revision", "{parameters[revision]}" ]},
		{ "name": "clean", "command": project_script + [ "clean" ] },
		{ "name": "develop", "command": project_script + [ "develop" ] },
		{ "name": "test", "command": project_script + [ "test" ] },
		{ "name": "lint", "command": project_script + [ "lint" ] },
	]

	return job


def distribute():
	job = {
		"identifier": "build-service_distribute",
		"description": "Generate and upload distribution packages for the BuildService project.",
		"workspace": "build-service",

		"properties": {
			"project": "build-service",
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_script = [ "{environment[python3_executable]}", "-u", "{environment[script_root]}/build_service.py", "--results", "{result_file_path}" ]
	project_script = [ ".venv/scripts/python", "-u", "scripts/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_script + [ "--repository", repository, "--revision", "{parameters[revision]}" ]},
		{ "name": "clean", "command": project_script + [ "clean" ] },
		{ "name": "develop", "command": project_script + [ "develop" ] },
		{ "name": "test", "command": project_script + [ "test" ] },
		{ "name": "lint", "command": project_script + [ "lint" ] },
		{ "name": "package", "command": project_script + [ "distribute", "--command", "package"] },
		{ "name": "upload", "command": project_script + [ "distribute", "--command", "upload"] },
	]

	return job
