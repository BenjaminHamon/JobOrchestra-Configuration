repository = "https://github.com/BenjaminHamon/Overmind.ImageManager"

controller_script = "bhamon_orchestra_worker_scripts.controller"
initialization_script = "bhamon_orchestra_worker_scripts.image_manager"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_project(environment):
	return {
		"identifier": "image-manager",
		"display_name": "Image Manager",
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
			"branches_for_status": [ "master", "develop" ],
		}
	}


def configure_jobs():
	return [
		controller(),
		package("debug"),
		package("release"),
		release(),
	]


def controller():
	job = {
		"identifier": "controller",
		"display_name": "Controller",
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
	controller_entry_point += [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	trigger_source_parameters = [ "--source-project", "{project_identifier}", "--source-run", "{run_identifier}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters },
		{ "name": "trigger_package_debug", "command": controller_entry_point + [ "trigger", "--project", "image-manager", "--job", "package_debug" ] + trigger_source_parameters },
		{ "name": "trigger_package_release", "command": controller_entry_point + [ "trigger", "--project", "image-manager", "--job", "package_release" ] + trigger_source_parameters },
		{ "name": "wait", "command": controller_entry_point + [ "wait" ] },
	]

	return job


def package(configuration):
	job = {
		"identifier": "package_%s" % configuration,
		"display_name": "Package %s" % configuration.capitalize(),
		"description": "Build and package the ImageManager project with the %s configuration." % configuration.capitalize(),

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
		{ "name": "compile", "command": project_entry_point + [ "compile", "--configuration", configuration.capitalize() ] },
		{ "name": "test", "command": project_entry_point + [ "test", "--configuration", configuration.capitalize() ] },
		{ "name": "package", "command": project_entry_point + [ "artifact", "package", "package", "--parameters", "configuration=" + configuration.capitalize() ] },
		{ "name": "verify", "command": project_entry_point + [ "artifact", "verify", "package", "--parameters", "configuration=" + configuration.capitalize() ] },
		{ "name": "upload", "command": project_entry_point + [ "artifact", "upload", "package", "--parameters", "configuration=" + configuration.capitalize() ] },
	]

	return job


def release():
	job = {
		"identifier": "release",
		"display_name": "Release",
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
