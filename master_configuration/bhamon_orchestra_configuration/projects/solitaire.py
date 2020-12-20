repository = "https://github.com/BenjaminHamon/Overmind.Solitaire"

controller_script = "bhamon_orchestra_worker_scripts.controller"
initialization_script = "bhamon_orchestra_worker_scripts.solitaire"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_project(environment):
	return {
		"identifier": "solitaire",
		"display_name": "Solitaire",
		"jobs": configure_jobs(),
		"schedules": [],
		"services": configure_services(environment),
	}


def configure_services(environment):
	return {
		"artifact_repository": {
			"url": environment["artifact_server_url"] + "/" + "Solitaire",
			"file_types": {
				"package": { "path_in_repository": "Packages", "file_extension": ".zip" },
			},
		},

		"revision_control": {
			"type": "github",
			"repository": "BenjaminHamon/Overmind.Solitaire",
			"branches_for_status": [ "master", "develop" ],
		}
	}


def configure_jobs():
	return [
		controller(),
		package("android", "debug"),
		package("android", "release"),
		package("linux", "debug"),
		package("linux", "release"),
		package("windows", "debug"),
		package("windows", "release"),
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
		"description": "Trigger all jobs for the Solitaire project.",

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				controller_entry_point + [ "trigger", "--project", "solitaire", "--job", "package_android_debug" ] + trigger_source_parameters,
				controller_entry_point + [ "trigger", "--project", "solitaire", "--job", "package_android_release" ] + trigger_source_parameters,
				controller_entry_point + [ "trigger", "--project", "solitaire", "--job", "package_linux_debug" ] + trigger_source_parameters,
				controller_entry_point + [ "trigger", "--project", "solitaire", "--job", "package_linux_release" ] + trigger_source_parameters,
				controller_entry_point + [ "trigger", "--project", "solitaire", "--job", "package_windows_debug" ] + trigger_source_parameters,
				controller_entry_point + [ "trigger", "--project", "solitaire", "--job", "package_windows_release" ] + trigger_source_parameters,
				controller_entry_point + [ "wait" ],
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},
	}

	return job


def package(target_platform, configuration):
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]
	artifact_parameters = [ "package", "--parameters", "platform=" + target_platform.capitalize(), "configuration=" + configuration.capitalize() ]

	job = {
		"identifier": "package_%s_%s" % (target_platform, configuration),
		"display_name": "Package %s %s" % (target_platform.capitalize(), configuration.capitalize()),
		"description": "Build and package the Solitaire project for %s and with the %s configuration." % (target_platform.capitalize(), configuration.capitalize()),

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				project_entry_point + [ "clean" ],
				project_entry_point + [ "develop" ],
				project_entry_point + [ "reimport", "--platform", target_platform.capitalize() ],
				project_entry_point + [ "build-asset-bundles", "--platform", target_platform.capitalize() ],
				project_entry_point + [ "build-package", "--platform", target_platform.capitalize(), "--configuration", configuration.capitalize() ],
				project_entry_point + [ "artifact", "package+verify+upload" ] + artifact_parameters,
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}

	return job
