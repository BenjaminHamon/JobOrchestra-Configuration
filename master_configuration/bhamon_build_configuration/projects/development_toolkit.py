repository = "https://github.com/BenjaminHamon/DevelopmentToolkit"

initialization_script = "{environment[build_worker_script_root]}/development_toolkit.py"
worker_configuration_path = "{environment[build_worker_configuration]}"
worker_python_executable = "{environment[build_worker_python_executable]}"


def configure_services(environment):
	return {
		"artifact_repository": {
			"url": environment["artifact_server_url"] + "/" + "DevelopmentToolkit",
		},

		"python_package_repository": {
			"url": environment["python_package_repository_url"],
			"distribution_extension": "-py3-none-any.whl",
		},

		"revision_control": {
			"service": "github",
			"owner": "BenjaminHamon",
			"repository": "DevelopmentToolkit",
		}
	}


def configure_jobs():
	return [
		check(),
		distribute(),
	]


def check():
	job = {
		"identifier": "development-toolkit_check",
		"description": "Run checks for the DevelopmentToolkit project.",
		"workspace": "development-toolkit",

		"properties": {
			"project": "development-toolkit",
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters},
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "develop", "command": project_entry_point + [ "develop" ] },
		{ "name": "lint", "command": project_entry_point + [ "lint" ] },
	]

	return job


def distribute():
	job = {
		"identifier": "development-toolkit_distribute",
		"description": "Generate and upload distribution packages for the DevelopmentToolkit project.",
		"workspace": "development-toolkit",

		"properties": {
			"project": "development-toolkit",
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters},
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "develop", "command": project_entry_point + [ "develop" ] },
		{ "name": "lint", "command": project_entry_point + [ "lint" ] },
		{ "name": "package", "command": project_entry_point + [ "distribute", "package"] },
		{ "name": "upload", "command": project_entry_point + [ "distribute", "upload"] },
	]

	return job