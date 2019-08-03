repository = "https://github.com/BenjaminHamon/Overmind.ImageManager"

controller_script = "{environment[build_worker_script_root]}/controller.py"
initialization_script = "{environment[build_worker_script_root]}/image_manager.py"
worker_configuration_path = "{environment[build_worker_configuration]}"
worker_python_executable = "{environment[build_worker_python_executable]}"


def configure_services(environment):
	return {
		"artifact_repository": {
			"url": environment["artifact_server_url"] + "/" + "ImageManager",
			"file_types": {
				"binaries": { "path_in_repository": "Binaries", "file_extension": ".zip" },
				"package": { "path_in_repository": "Packages", "file_extension": ".zip" },
				"package_final": { "path_in_repository": "Packages", "file_extension": ".zip" },
			},
		},

		"revision_control": {
			"service": "github",
			"owner": "BenjaminHamon",
			"repository": "Overmind.ImageManager",
		}
	}


def configure_jobs():
	return [
		controller(),
		package(),
	]


def controller():
	job = {
		"identifier": "image-manager_controller",
		"description": "Trigger all jobs for the ImageManager project.",
		"workspace": "image-manager",

		"properties": {
			"project": "image-manager",
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "controller", "--repository", repository, "--revision", "{parameters[revision]}" ]
	controller_entry_point = [ worker_python_executable, "-u", controller_script ]
	controller_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]

	package_job = "image-manager_package"
	package_debug_parameters = [ "--parameters", "configuration=Debug", "revision={results[revision_control][revision]}" ]
	package_release_parameters = [ "--parameters", "configuration=Release", "revision={results[revision_control][revision]}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters },
		{ "name": "trigger_package_debug", "command": controller_entry_point + controller_parameters + [ "trigger", package_job ] + package_debug_parameters },
		{ "name": "trigger_package_release", "command": controller_entry_point + controller_parameters + [ "trigger", package_job ] + package_release_parameters },
		{ "name": "wait", "command": controller_entry_point + controller_parameters + [ "wait" ] },
	]

	return job


def package():
	job = {
		"identifier": "image-manager_package",
		"description": "Build and package the ImageManager project.",
		"workspace": "image-manager",

		"properties": {
			"project": "image-manager",
			"operating_system": [ "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
			{ "key": "configuration", "description": "Project configuration" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "Scripts/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]
	artifact_parameters = [ "package", "--parameters", "configuration={parameters[configuration]}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters },
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "metadata", "command": project_entry_point + [ "metadata" ] },
		{ "name": "compile", "command": project_entry_point + [ "compile", "--configuration", "{parameters[configuration]}" ] },
		{ "name": "test", "command": project_entry_point + [ "test", "--configuration", "{parameters[configuration]}" ] },
		{ "name": "package", "command": project_entry_point + [ "artifact", "package" ] + artifact_parameters },
		{ "name": "verify", "command": project_entry_point + [ "artifact", "verify" ] + artifact_parameters },
		{ "name": "upload", "command": project_entry_point + [ "artifact", "upload" ] + artifact_parameters },
	]

	return job
