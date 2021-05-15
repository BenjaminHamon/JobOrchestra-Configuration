repository = "https://github.com/BenjaminHamon/Overmind.ImageManager"

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
			"references_for_status": [ "master", "develop" ],
		}
	}


def configure_jobs():
	return [
		development_pipeline(),
		release_pipeline(),
		build("debug"),
		build("release"),
		release(),
	]


def development_pipeline():
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "controller", "--repository", repository, "--revision", "{parameters[revision]}" ]

	job = {
		"identifier": "development_pipeline",
		"display_name": "Development Pipeline",
		"description": "Run jobs for development.",

		"definition": {
			"type": "pipeline",

			"setup_commands": [
				initialization_entry_point + initialization_parameters,
			],

			"elements": [
				{
					"identifier": "build_debug",
					"job": "build_debug",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "build_release",
					"job": "build_release",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
			"include_in_status": True,
		},
	}

	return job


def release_pipeline():
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "controller", "--repository", repository, "--revision", "{parameters[revision]}" ]

	job = {
		"identifier": "release_pipeline",
		"display_name": "Release Pipeline",
		"description": "Run jobs for release.",

		"definition": {
			"type": "pipeline",

			"setup_commands": [
				initialization_entry_point + initialization_parameters,
			],

			"elements": [
				{
					"identifier": "build_debug",
					"job": "build_debug",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "build_release",
					"job": "build_release",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "release",
					"job": "release",
					"parameters": { "revision": "{results[revision_control][revision]}" },

					"after": [
						{ "element": "build_debug", "status": [ "succeeded" ] },
						{ "element": "build_release", "status": [ "succeeded" ] },
					],
				},
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
			"include_in_status": True,
		},
	}

	return job


def build(configuration):
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job = {
		"identifier": "build_%s" % configuration,
		"display_name": "Build %s" % configuration.capitalize(),
		"description": "Build the ImageManager project with the %s configuration." % configuration.capitalize(),

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				project_entry_point + [ "clean" ],
				project_entry_point + [ "develop" ],
				project_entry_point + [ "metadata" ],
				project_entry_point + [ "compile", "--configuration", configuration.capitalize() ],
				project_entry_point + [ "test", "--configuration", configuration.capitalize() ],
				project_entry_point + [ "artifact", "package+verify+upload", "binaries", "--parameters", "assembly=WallpaperService", "configuration=" + configuration.capitalize() ],
				project_entry_point + [ "artifact", "package+verify+upload", "binaries", "--parameters", "assembly=WindowsClient", "configuration=" + configuration.capitalize() ],
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "windows" ],
			"is_controller": False,
			"include_in_status": False,
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
		"description": "Package the ImageManager project for release.",

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				project_entry_point + [ "clean" ],
				project_entry_point + [ "develop" ],
				project_entry_point + [ "artifact", "download+install", "binaries", "--parameters", "assembly=WallpaperService", "configuration=Release" ],
				project_entry_point + [ "artifact", "download+install", "binaries", "--parameters", "assembly=WindowsClient", "configuration=Release" ],
				project_entry_point + [ "artifact", "package+verify+upload", "package_final", "--parameters", "configuration=Release" ],
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "windows" ],
			"is_controller": False,
			"include_in_status": False,
		},
	}

	return job
