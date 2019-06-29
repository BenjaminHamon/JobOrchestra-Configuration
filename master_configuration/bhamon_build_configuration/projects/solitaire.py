repository = "https://github.com/BenjaminHamon/Overmind.Solitaire"


def configure_services():
	return {
		"revision_control": {
			"service": "github",
			"parameters": {
				"owner": "BenjaminHamon",
				"repository": "Overmind.Solitaire",
			},
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
		"identifier": "solitaire_controller",
		"description": "Trigger all jobs for the Solitaire project.",
		"workspace": "solitaire",

		"properties": {
			"project": "solitaire",
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],
	}

	initialization_script = [ "{environment[python3_executable]}", "-u", "{environment[script_root]}/solitaire.py" ]
	initialization_script += [ "--results", "{result_file_path}" ]

	controller_script = [ "{environment[python3_executable]}", "-u", "{environment[script_root]}/controller.py" ]
	controller_script += [ "--service-url", "{environment[build_service_url]}", "--results", "{result_file_path}" ]

	package_android_job = "solitaire_package_android"
	package_linux_job = "solitaire_package_linux"
	package_windows_job = "solitaire_package_windows"
	package_debug_parameters = [ "--parameters", "configuration=Debug", "revision={results[revision_control][revision]}" ]
	package_release_parameters = [ "--parameters", "configuration=Release", "revision={results[revision_control][revision]}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_script + [ "--repository", repository, "--revision", "{parameters[revision]}", "--type", "controller" ] },
		{ "name": "trigger_package_android_debug", "command": controller_script + [ "trigger", package_android_job ] + package_debug_parameters },
		{ "name": "trigger_package_android_release", "command": controller_script + [ "trigger", package_android_job ] + package_release_parameters },
		{ "name": "trigger_package_linux_debug", "command": controller_script + [ "trigger", package_linux_job ] + package_debug_parameters },
		{ "name": "trigger_package_linux_release", "command": controller_script + [ "trigger", package_linux_job ] + package_release_parameters },
		{ "name": "trigger_package_windows_debug", "command": controller_script + [ "trigger", package_windows_job ] + package_debug_parameters },
		{ "name": "trigger_package_windows_release", "command": controller_script + [ "trigger", package_windows_job ] + package_release_parameters },
		{ "name": "wait", "command": controller_script + [ "wait" ] },
	]

	return job


def package(target_platform):
	job = {
		"identifier": "solitaire_package_" + target_platform.lower(),
		"description": "Build and package the Solitaire project.",
		"workspace": "solitaire",

		"properties": {
			"project": "solitaire",
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
			{ "key": "configuration", "description": "Package configuration" },
		],
	}

	initialization_script = [ "{environment[python3_executable]}", "-u", "{environment[script_root]}/solitaire.py", "--results", "{result_file_path}" ]
	project_script = [ ".venv/scripts/python", "-u", "Scripts/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]
	artifact_parameters = [ "--parameters", "platform=" + target_platform, "configuration={parameters[configuration]}" ]

	job["steps"] = [
		{ "name": "initialize", "command": initialization_script + [ "--repository", repository, "--revision", "{parameters[revision]}", "--type", "worker" ]},
		{ "name": "clean", "command": project_script + [ "clean" ] },
		{ "name": "build", "command": project_script + [ "package", "--platform", target_platform, "--configuration", "{parameters[configuration]}" ] },
		{ "name": "package", "command": project_script + [ "artifact", "package", "--command", "package" ] + artifact_parameters },
		{ "name": "verify", "command": project_script + [ "artifact", "package", "--command", "verify" ] + artifact_parameters },
		{ "name": "upload", "command": project_script + [ "artifact", "package", "--command", "upload" ] + artifact_parameters },
	]

	return job
