repository = "https://github.com/BenjaminHamon/MyWebsite"

initialization_script = "bhamon_orchestra_worker_scripts.my_website"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_project(environment):
	return {
		"identifier": "my-website",
		"display_name": "My Website",
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
			"branches_for_status": [ "master", "develop" ],
		}
	}


def configure_jobs():
	return [
		check(),
		distribute(),
	]


def check():
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job = {
		"identifier": "check",
		"display_name": "Check",
		"description": "Run checks for the MyWebsite project.",

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				project_entry_point + [ "clean" ],
				project_entry_point + [ "develop" ],
				project_entry_point + [ "lint" ],
			],
		},

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
			"include_in_status": True,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	return job


def distribute():
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job = {
		"identifier": "distribute",
		"display_name": "Distribute",
		"description": "Generate and upload distribution packages for the MyWebsite project.",

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				project_entry_point + [ "clean" ],
				project_entry_point + [ "develop" ],
				project_entry_point + [ "lint" ],
				project_entry_point + [ "distribute", "package"],
				project_entry_point + [ "distribute", "upload"],
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
			"include_in_status": True,
		},
	}

	return job
