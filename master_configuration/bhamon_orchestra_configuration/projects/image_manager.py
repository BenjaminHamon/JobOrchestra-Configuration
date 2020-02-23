repository = "https://github.com/BenjaminHamon/Overmind.ImageManager"

controller_script = "bhamon_orchestra_worker_scripts.controller"
initialization_script = "bhamon_orchestra_worker_scripts.image_manager"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_project(environment):
	return {
		"identifier": "image-manager",
		"jobs": configure_jobs(),
		"schedules": [],
		"services": configure_services(environment),
	}


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
			"type": "github",
			"repository": "BenjaminHamon/Overmind.ImageManager",
		}
	}


def configure_jobs():
	return [
		controller(),
		package(),
		release(),
	]


def controller():
	job = {
		"identifier": "controller",
		"description": "Trigger all jobs for the ImageManager project.",
		"workspace": "image-manager",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "controller", "--repository", repository, "--revision", "{parameters[revision]}" ]
	controller_entry_point = [ worker_python_executable, "-u", "-m", controller_script ]
	controller_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]

	package_debug_parameters = [ "--parameters", "configuration=Debug", "revision={results[revision_control][revision]}" ]
	package_release_parameters = [ "--parameters", "configuration=Release", "revision={results[revision_control][revision]}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters },
		{ "name": "trigger_package_debug", "command": controller_entry_point + controller_parameters + [ "trigger", "image-manager", "package" ] + package_debug_parameters },
		{ "name": "trigger_package_release", "command": controller_entry_point + controller_parameters + [ "trigger", "image-manager", "package" ] + package_release_parameters },
		{ "name": "wait", "command": controller_entry_point + controller_parameters + [ "wait" ] },
	]

	return job


def package():
	job = {
		"identifier": "package",
		"description": "Build and package the ImageManager project.",
		"workspace": "image-manager",

		"properties": {
			"operating_system": [ "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
			{ "key": "configuration", "description": "Project configuration" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters },
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "develop", "command": project_entry_point + [ "develop" ] },
		{ "name": "metadata", "command": project_entry_point + [ "metadata" ] },
		{ "name": "compile", "command": project_entry_point + [ "compile", "--configuration", "{parameters[configuration]}" ] },
		{ "name": "test", "command": project_entry_point + [ "test", "--configuration", "{parameters[configuration]}" ] },
		{ "name": "package", "command": project_entry_point + [ "artifact", "package", "package", "--parameters", "configuration={parameters[configuration]}" ] },
		{ "name": "verify", "command": project_entry_point + [ "artifact", "verify", "package", "--parameters", "configuration={parameters[configuration]}" ] },
		{ "name": "upload", "command": project_entry_point + [ "artifact", "upload", "package", "--parameters", "configuration={parameters[configuration]}" ] },
	]

	return job


def release():
	job = {
		"identifier": "release",
		"description": "Build and package the ImageManager project for release.",
		"workspace": "image-manager",

		"properties": {
			"operating_system": [ "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters },
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "develop", "command": project_entry_point + [ "develop" ] },
		{ "name": "metadata", "command": project_entry_point + [ "metadata" ] },
		{ "name": "compile debug", "command": project_entry_point + [ "compile", "--configuration", "Debug" ] },
		{ "name": "test debug", "command": project_entry_point + [ "test", "--configuration", "Debug" ] },
		{ "name": "compile release", "command": project_entry_point + [ "compile", "--configuration", "Release" ] },
		{ "name": "test release", "command": project_entry_point + [ "test", "--configuration", "Release" ] },
		{ "name": "artifact package package debug", "command": project_entry_point + [ "artifact", "package", "package", "--parameters", "configuration=Debug" ] },
		{ "name": "artifact verify package debug", "command": project_entry_point + [ "artifact", "verify", "package", "--parameters", "configuration=Debug" ] },
		{ "name": "artifact upload package debug", "command": project_entry_point + [ "artifact", "upload", "package", "--parameters", "configuration=Debug" ] },
		{ "name": "artifact package package release", "command": project_entry_point + [ "artifact", "package", "package", "--parameters", "configuration=Release" ] },
		{ "name": "artifact verify package release", "command": project_entry_point + [ "artifact", "verify", "package", "--parameters", "configuration=Release" ] },
		{ "name": "artifact upload package release", "command": project_entry_point + [ "artifact", "upload", "package", "--parameters", "configuration=Release" ] },
		{ "name": "artifact package package final", "command": project_entry_point + [ "artifact", "package", "package_final", "--parameters", "configuration=Release" ] },
		{ "name": "artifact verify package final", "command": project_entry_point + [ "artifact", "verify", "package_final", "--parameters", "configuration=Release" ] },
		{ "name": "artifact upload package final", "command": project_entry_point + [ "artifact", "upload", "package_final", "--parameters", "configuration=Release" ] },
	]

	return job
