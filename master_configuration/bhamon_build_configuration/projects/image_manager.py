repository = "https://github.com/BenjaminHamon/Overmind.ImageManager"


def configure_services(environment):
	return {
		"artifact_repository": {
			"url": environment["artifact_repository_url"] + "/" + "ImageManager",
			"file_types": {
				"binaries": { "path_in_repository": "Binaries", "file_extension": ".zip" },
				"package": { "path_in_repository": "Packages", "file_extension": ".zip" },
				"package_final": { "path_in_repository": "Packages", "file_extension": ".zip" },
			},
		},

		"revision_control": {
			"service": "github",
			"parameters": {
				"owner": "BenjaminHamon",
				"repository": "Overmind.ImageManager",
			},
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

	initialization_script = [ "{environment[build_worker_python_executable]}", "-u", "{environment[build_worker_script_root]}/image_manager.py", "--results", "{result_file_path}" ]
	controller_script = [ "{environment[build_worker_python_executable]}", "-u", "{environment[build_worker_script_root]}/controller.py", "--results", "{result_file_path}" ]

	package_job = "image-manager_package"
	package_debug_parameters = [ "--parameters", "configuration=Debug", "revision={results[revision_control][revision]}" ]
	package_release_parameters = [ "--parameters", "configuration=Release", "revision={results[revision_control][revision]}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_script + [ "--repository", repository, "--revision", "{parameters[revision]}", "--type", "controller" ] },
		{ "name": "trigger_package_debug", "command": controller_script + [ "trigger", package_job ] + package_debug_parameters },
		{ "name": "trigger_package_release", "command": controller_script + [ "trigger", package_job ] + package_release_parameters },
		{ "name": "wait", "command": controller_script + [ "wait" ] },
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

	initialization_script = [ "{environment[build_worker_python_executable]}", "-u", "{environment[build_worker_script_root]}/image_manager.py", "--results", "{result_file_path}" ]
	project_script = [ ".venv/scripts/python", "-u", "Scripts/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_script + [ "--repository", repository, "--revision", "{parameters[revision]}", "--type", "worker" ]},
		{ "name": "clean", "command": project_script + [ "clean" ] },
		{ "name": "metadata", "command": project_script + [ "metadata" ] },
		{ "name": "compile", "command": project_script + [ "compile", "--configuration", "{parameters[configuration]}" ] },
		{ "name": "test", "command": project_script + [ "test", "--configuration", "{parameters[configuration]}" ] },
		{ "name": "package", "command": project_script + [ "artifact", "package", "--command", "package", "--parameters", "configuration={parameters[configuration]}" ] },
		{ "name": "verify", "command": project_script + [ "artifact", "package", "--command", "verify", "--parameters", "configuration={parameters[configuration]}" ] },
		{ "name": "upload", "command": project_script + [ "artifact", "package", "--command", "upload", "--parameters", "configuration={parameters[configuration]}" ] },
	]

	return job
