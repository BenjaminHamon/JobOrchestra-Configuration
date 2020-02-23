repository = "https://github.com/BenjaminHamon/Overmind.Solitaire"

controller_script = "bhamon_orchestra_worker_scripts.controller"
initialization_script = "bhamon_orchestra_worker_scripts.solitaire"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_project(environment):
	return {
		"identifier": "solitaire",
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
		}
	}


def configure_jobs():
	return [
		controller(),
		package("Android"),
		package("Linux"),
		package("Windows"),
	]


def controller():
	job = {
		"identifier": "controller",
		"description": "Trigger all jobs for the Solitaire project.",
		"workspace": "solitaire",

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
		{ "name": "trigger_package_android_debug", "command": controller_entry_point + controller_parameters + [ "trigger", "solitaire", "package_android" ] + package_debug_parameters },
		{ "name": "trigger_package_android_release", "command": controller_entry_point + controller_parameters + [ "trigger", "solitaire", "package_android" ] + package_release_parameters },
		{ "name": "trigger_package_linux_debug", "command": controller_entry_point + controller_parameters + [ "trigger", "solitaire", "package_linux" ] + package_debug_parameters },
		{ "name": "trigger_package_linux_release", "command": controller_entry_point + controller_parameters + [ "trigger", "solitaire", "package_linux" ] + package_release_parameters },
		{ "name": "trigger_package_windows_debug", "command": controller_entry_point + controller_parameters + [ "trigger", "solitaire", "package_windows" ] + package_debug_parameters },
		{ "name": "trigger_package_windows_release", "command": controller_entry_point + controller_parameters + [ "trigger", "solitaire", "package_windows" ] + package_release_parameters },
		{ "name": "wait", "command": controller_entry_point + controller_parameters + [ "wait" ] },
	]

	return job


def package(target_platform):
	job = {
		"identifier": "package_%s" % target_platform.lower(),
		"description": "Build and package the Solitaire project.",
		"workspace": "solitaire",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
			{ "key": "configuration", "description": "Package configuration" },
		],
	}

	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "Scripts/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]
	artifact_parameters = [ "package", "--parameters", "platform=" + target_platform, "configuration={parameters[configuration]}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_entry_point + initialization_parameters },
		{ "name": "clean", "command": project_entry_point + [ "clean" ] },
		{ "name": "build", "command": project_entry_point + [ "package", "--platform", target_platform, "--configuration", "{parameters[configuration]}" ] },
		{ "name": "package", "command": project_entry_point + [ "artifact", "package" ] + artifact_parameters },
		{ "name": "verify", "command": project_entry_point + [ "artifact", "verify" ] + artifact_parameters },
		{ "name": "upload", "command": project_entry_point + [ "artifact", "upload" ] + artifact_parameters },
	]

	return job
