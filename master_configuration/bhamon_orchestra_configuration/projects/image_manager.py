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
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "controller", "--repository", repository, "--revision", "{parameters[revision]}" ]
	controller_entry_point = [ worker_python_executable, "-u", "-m", controller_script ]
	controller_entry_point += [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	trigger_source_parameters = [ "--source-project", "{project_identifier}", "--source-run", "{run_identifier}" ]

	job = {
		"identifier": "controller",
		"display_name": "Controller",
		"description": "Trigger all jobs for the ImageManager project.",

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				controller_entry_point + [ "trigger", "--project", "image-manager", "--job", "package_debug" ] + trigger_source_parameters,
				controller_entry_point + [ "trigger", "--project", "image-manager", "--job", "package_release" ] + trigger_source_parameters,
				controller_entry_point + [ "wait" ],
			],
		},

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	return job


def package(configuration):
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job = {
		"identifier": "package_%s" % configuration,
		"display_name": "Package %s" % configuration.capitalize(),
		"description": "Build and package the ImageManager project with the %s configuration." % configuration.capitalize(),

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				project_entry_point + [ "clean" ],
				project_entry_point + [ "develop" ],
				project_entry_point + [ "metadata" ],
				project_entry_point + [ "compile", "--configuration", configuration.capitalize() ],
				project_entry_point + [ "test", "--configuration", configuration.capitalize() ],
				project_entry_point + [ "artifact", "package", "package", "--parameters", "configuration=" + configuration.capitalize() ],
				project_entry_point + [ "artifact", "verify", "package", "--parameters", "configuration=" + configuration.capitalize() ],
				project_entry_point + [ "artifact", "upload", "package", "--parameters", "configuration=" + configuration.capitalize() ],
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "windows" ],
			"is_controller": False,
		},
	}

	return job


def release():
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job = {
		"identifier": "release",
		"display_name": "Release",
		"description": "Build and package the ImageManager project for release.",

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				project_entry_point + [ "clean" ],
				project_entry_point + [ "develop" ],
				project_entry_point + [ "metadata" ],
				project_entry_point + [ "compile", "--configuration", "Debug" ],
				project_entry_point + [ "test", "--configuration", "Debug" ],
				project_entry_point + [ "compile", "--configuration", "Release" ],
				project_entry_point + [ "test", "--configuration", "Release" ],
				project_entry_point + [ "artifact", "package", "package", "--parameters", "configuration=Debug" ],
				project_entry_point + [ "artifact", "verify", "package", "--parameters", "configuration=Debug" ],
				project_entry_point + [ "artifact", "upload", "package", "--parameters", "configuration=Debug" ],
				project_entry_point + [ "artifact", "package", "package", "--parameters", "configuration=Release" ],
				project_entry_point + [ "artifact", "verify", "package", "--parameters", "configuration=Release" ],
				project_entry_point + [ "artifact", "upload", "package", "--parameters", "configuration=Release" ],
				project_entry_point + [ "artifact", "package", "package_final", "--parameters", "configuration=Release" ],
				project_entry_point + [ "artifact", "verify", "package_final", "--parameters", "configuration=Release" ],
				project_entry_point + [ "artifact", "upload", "package_final", "--parameters", "configuration=Release" ],
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "windows" ],
			"is_controller": False,
		},
	}

	return job
