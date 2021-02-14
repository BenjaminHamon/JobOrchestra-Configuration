repository = "https://github.com/BenjaminHamon/JobOrchestra-Configuration"

initialization_script = "bhamon_orchestra_worker_scripts.job_orchestra_configuration"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_project(environment):
	return {
		"identifier": "job-orchestra-configuration",
		"display_name": "Job Orchestra Configuration",
		"jobs": configure_jobs(),
		"schedules": [],
		"services": configure_services(environment),
	}


def configure_services(environment):
	return {
		"artifact_repository": {
			"url": environment["artifact_server_url"] + "/" + "JobOrchestra-Configuration",
			"file_types": {
				"package": { "path_in_repository": "packages", "file_extension": ".zip" },
			},
		},

		"python_package_repository": {
			"url": environment["python_package_repository_url"],
			"distribution_extension": "-py3-none-any.whl",
		},

		"revision_control": {
			"type": "github",
			"repository": "BenjaminHamon/JobOrchestra-Configuration",
			"branches_for_status": [ "master", "develop" ],
		}
	}


def configure_jobs():
	return [
		development_pipeline(),
		release_pipeline(),
		check("linux", "3.7"),
		check("linux", "3.8"),
		check("linux", "3.9"),
		check("windows", "3.7"),
		check("windows", "3.8"),
		check("windows", "3.9"),
		package(),
		distribute(),
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
					"identifier": "check_linux_python-3.7",
					"job": "check_linux_python-3.7",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "check_linux_python-3.8",
					"job": "check_linux_python-3.8",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "check_linux_python-3.9",
					"job": "check_linux_python-3.9",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "check_windows_python-3.7",
					"job": "check_windows_python-3.7",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "check_windows_python-3.8",
					"job": "check_windows_python-3.8",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "check_windows_python-3.9",
					"job": "check_windows_python-3.9",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "package",
					"job": "package",
					"parameters": { "revision": "{results[revision_control][revision]}" },

					"after": [
						{ "element": "check_linux_python-3.7", "status": "succeeded" },
						{ "element": "check_linux_python-3.8", "status": "succeeded" },
						{ "element": "check_linux_python-3.9", "status": "succeeded" },
						{ "element": "check_windows_python-3.7", "status": "succeeded" },
						{ "element": "check_windows_python-3.8", "status": "succeeded" },
						{ "element": "check_windows_python-3.9", "status": "succeeded" },
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
					"identifier": "check_linux_python-3.7",
					"job": "check_linux_python-3.7",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "check_linux_python-3.8",
					"job": "check_linux_python-3.8",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "check_linux_python-3.9",
					"job": "check_linux_python-3.9",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "check_windows_python-3.7",
					"job": "check_windows_python-3.7",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "check_windows_python-3.8",
					"job": "check_windows_python-3.8",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "check_windows_python-3.9",
					"job": "check_windows_python-3.9",
					"parameters": { "revision": "{results[revision_control][revision]}" },
				},

				{
					"identifier": "package",
					"job": "package",
					"parameters": { "revision": "{results[revision_control][revision]}" },

					"after": [
						{ "element": "check_linux_python-3.7", "status": "succeeded" },
						{ "element": "check_linux_python-3.8", "status": "succeeded" },
						{ "element": "check_linux_python-3.9", "status": "succeeded" },
						{ "element": "check_windows_python-3.7", "status": "succeeded" },
						{ "element": "check_windows_python-3.8", "status": "succeeded" },
						{ "element": "check_windows_python-3.9", "status": "succeeded" },
					],
				},

				{
					"identifier": "distribute",
					"job": "distribute",
					"parameters": { "revision": "{results[revision_control][revision]}" },

					"after": [
						{ "element": "package", "status": "succeeded" },
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


def check(platform, python_version):
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	initialization_parameters += [ "--python-version", python_version ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job = {
		"identifier": "check_%s_python-%s" % (platform, python_version),
		"display_name": "Check for %s with Python %s" % (platform.capitalize(), python_version),
		"description": "Run checks for the JobOrchestra-Configuration project on %s." % platform.capitalize(),

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				project_entry_point + [ "clean" ],
				project_entry_point + [ "develop" ],
				project_entry_point + [ "lint" ],
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ platform ],
			"is_controller": False,
			"include_in_status": False,
		},
	}

	return job


def package():
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job = {
		"identifier": "package",
		"display_name": "Package",
		"description": "Generate distribution packages for the JobOrchestra-Configuration project.",

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				project_entry_point + [ "clean" ],
				project_entry_point + [ "develop" ],
				project_entry_point + [ "distribute", "package" ],
				project_entry_point + [ "artifact", "package+verify+upload", "package" ],
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
			"include_in_status": False,
		},
	}

	return job


def distribute():
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	initialization_parameters += [ "--type", "worker", "--repository", repository, "--revision", "{parameters[revision]}" ]
	project_entry_point = [ ".venv/scripts/python", "-u", "development/main.py", "--verbosity", "debug", "--results", "{result_file_path}" ]

	job = {
		"identifier": "distribute",
		"display_name": "Distribute",
		"description": "Upload distribution packages for the JobOrchestra-Configuration project to the python package repository.",

		"definition": {
			"type": "job",

			"commands": [
				initialization_entry_point + initialization_parameters,
				project_entry_point + [ "clean" ],
				project_entry_point + [ "develop" ],
				project_entry_point + [ "artifact", "download+install", "package" ],
				project_entry_point + [ "distribute", "upload" ],
			],
		},

		"parameters": [
			{ "key": "revision", "description": "Revision for the source repository" },
		],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
			"include_in_status": False,
		},
	}

	return job
