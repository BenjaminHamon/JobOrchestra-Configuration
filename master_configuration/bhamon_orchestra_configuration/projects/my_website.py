repository = "https://github.com/BenjaminHamon/MyWebsite"

initialization_script = "bhamon_orchestra_worker_scripts.my_website"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_project(environment):
	return {
		"identifier": "my-website",
		"jobs": configure_jobs(),
		"schedules": [],
		"services": configure_services(environment),
	}


def configure_services(environment):
	return {
		"artifact_repository": {
			"url": environment["artifact_server_url"] + "/" + "MyWebsite",
		},

		"python_package_repository": {
			"url": environment["python_package_repository_url"],
			"distribution_extension": "-py3-none-any.whl",
		},

		"revision_control": {
			"type": "github",
			"repository": "BenjaminHamon/MyWebsite",
		}
	}


def configure_jobs():
	return [
		check(),
		distribute(),
	]


def check():
	job = {
		"identifier": "check",
		"description": "Run checks for the MyWebsite project.",
		"workspace": "my-website",

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
	project_entry_point = [ ".venv/scripts/python", "-u", "scripts/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters},
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "develop", "command": project_entry_point + [ "develop" ] },
		{ "name": "lint", "command": project_entry_point + [ "lint" ] },
	]

	return job


def distribute():
	job = {
		"identifier": "distribute",
		"description": "Generate and upload distribution packages for the MyWebsite project.",
		"workspace": "my-website",

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
	project_entry_point = [ ".venv/scripts/python", "-u", "scripts/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters},
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "develop", "command": project_entry_point + [ "develop" ] },
		{ "name": "lint", "command": project_entry_point + [ "lint" ] },
		{ "name": "package", "command": project_entry_point + [ "distribute", "package"] },
		{ "name": "upload", "command": project_entry_point + [ "distribute", "upload"] },
	]

	return job
