controller_script = "bhamon_orchestra_worker_scripts.controller"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_project():
	return {
		"identifier": "example",
		"display_name": "Example",
		"jobs": configure_jobs(),
		"schedules": configure_schedules(),
		"services": {},
	}


def configure_jobs():
	return [
		empty(),
		hello(),
		sleep(),
		failure(),
		exception(),
		environment(),
		parameters(),
		log_with_special_characters(),
		log_with_html(),
		large_log(),
		large_log_random(),
		slow_log(),
		controller_success(),
		controller_failure(),
		pipeline_success(),
		pipeline_failure(),
		pipeline_complex_1(),
		pipeline_complex_2(),
		pipeline_complex_3(),
	]


def empty():
	return {
		"identifier": "empty",
		"display_name": "Empty",
		"description": "Example job doing nothing.",

		"definition": {
			"type": "job",
			"commands": [],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def hello():
	return {
		"identifier": "hello",
		"display_name": "Hello",
		"description": "Example job printing hello.",

		"definition": {
			"type": "job",

			"commands": [
				[ worker_python_executable, "-c", "print('hello')" ],
				[ worker_python_executable, "-c", "import sys; print('hello from stderr', file = sys.stderr)" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def sleep():
	return {
		"identifier": "sleep",
		"display_name": "Sleep",
		"description": "Example job sleeping for a few seconds.",

		"definition": {
			"type": "job",

			"commands": [
				[ worker_python_executable, "-c", "print('hello')" ],
				[ worker_python_executable, "-c", "import time; time.sleep(60)" ],
				[ worker_python_executable, "-c", "print('hello')" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def failure():
	return {
		"identifier": "failure",
		"display_name": "Failure",
		"description": "Example job with a failing step.",

		"definition": {
			"type": "job",

			"commands": [
				[ worker_python_executable, "-c", "print('hello')" ],
				[ worker_python_executable, "-c", "print('hello')" ],
				[ worker_python_executable, "-c", "raise RuntimeError" ],
				[ worker_python_executable, "-c", "print('hello')" ],
				[ worker_python_executable, "-c", "print('hello')" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def exception():
	return {
		"identifier": "exception",
		"display_name": "Exception",
		"description": "Example job with a configuration error.",

		"definition": {
			"type": "job",

			"commands": [
				[ worker_python_executable, "-c", "print('hello')" ],
				[ worker_python_executable, "-c", "print('hello')" ],
				[ worker_python_executable, "-c", "print('{undefined}')" ],
				[ worker_python_executable, "-c", "print('hello')" ],
				[ worker_python_executable, "-c", "print('hello')" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def environment():
	script = "bhamon_orchestra_worker_scripts.examples.environment"
	command = [ worker_python_executable, "-u", "-m", script ]
	command_parameters = [ "--configuration", worker_configuration_path ]

	return {
		"identifier": "environment",
		"display_name": "Environment",
		"description": "Example job using environment.",

		"definition": {
			"type": "job",

			"commands": [
				command + command_parameters,
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def parameters():
	return {
		"identifier": "parameters",
		"display_name": "Parameters",
		"description": "Example job with parameters.",

		"definition": {
			"type": "job",

			"commands": [
				[ worker_python_executable, "-c", "print('{parameters[text_to_print]}')" ],
			],
		},

		"parameters": [
			{ "key": "text_to_print", "description": "Text to write to log" },
		],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def log_with_special_characters():
	return {
		"identifier": "log-with-special-characters",
		"display_name": "Log with Special Characters",
		"description": "Example job generating log files containing special characters.",

		"definition": {
			"type": "job",

			"commands": [
				[ worker_python_executable, "-c", "print('… é ² √ 👍')" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def log_with_html():
	return {
		"identifier": "log-with-html",
		"display_name": "Log with HTML",
		"description": "Example job generating log files containing html.",

		"definition": {
			"type": "job",

			"commands": [
				[ worker_python_executable, "-c", "print('<p>hello</p>')" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def large_log():
	return {
		"identifier": "large-log",
		"display_name": "Large Log",
		"description": "Example job generating large log files.",

		"definition": {
			"type": "job",

			"commands": [
				[ worker_python_executable, "-c", "for i in range(1000 * 1000): print('Testing for large log files')" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def large_log_random():
	return {
		"identifier": "large-log-random",
		"display_name": "Large Log Random",
		"description": "Example job generating large log files with random content.",

		"definition": {
			"type": "job",

			"commands": [
				[ worker_python_executable, "-c", "exec('import uuid\\nfor i in range(1000 * 1000): print(uuid.uuid4())')" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def slow_log():
	return {
		"identifier": "slow_log",
		"display_name": "Slow Log",
		"description": "Example job generating a log over some time.",

		"definition": {
			"type": "job",

			"commands": [
				[ worker_python_executable, "-u", "-m", "bhamon_orchestra_worker_scripts.examples.slow_log" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},
	}


def controller_success():
	controller_entry_point = [ worker_python_executable, "-u", "-m", controller_script ]
	controller_entry_point += [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	trigger_source_parameters = [ "--source-project", "{project_identifier}", "--source-run", "{run_identifier}" ]

	return {
		"identifier": "controller-success",
		"display_name": "Controller Success",
		"description": "Example controller job.",

		"definition": {
			"type": "job",

			"commands": [
				controller_entry_point + [ "trigger", "--project", "example", "--job", "hello" ] + trigger_source_parameters,
				controller_entry_point + [ "trigger", "--project", "example", "--job", "sleep" ] + trigger_source_parameters,
				controller_entry_point + [ "trigger", "--project", "example", "--job", "hello" ] + trigger_source_parameters,
				controller_entry_point + [ "wait" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},
	}


def controller_failure():
	controller_entry_point = [ worker_python_executable, "-u", "-m", controller_script ]
	controller_entry_point += [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	trigger_source_parameters = [ "--source-project", "{project_identifier}", "--source-run", "{run_identifier}" ]

	return {
		"identifier": "controller-failure",
		"display_name": "Controller Failure",
		"description": "Example controller job.",

		"definition": {
			"type": "job",

			"commands": [
				controller_entry_point + [ "trigger", "--project", "example", "--job", "hello" ] + trigger_source_parameters,
				controller_entry_point + [ "trigger", "--project", "example", "--job", "sleep" ] + trigger_source_parameters,
				controller_entry_point + [ "trigger", "--project", "example", "--job", "failure" ] + trigger_source_parameters,
				controller_entry_point + [ "wait" ],
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},
	}


def pipeline_success():
	return {
		"identifier": "pipeline-success",
		"display_name": "Pipeline Success",
		"description": "Example pipeline job.",

		"definition": {
			"type": "pipeline",

			"elements": [
				{ "identifier": "hello-1", "job": "hello" },
				{ "identifier": "hello-2", "job": "hello", "after": [ { "element": "hello-1", "status": "succeeded" } ] },
				{ "identifier": "hello-3", "job": "hello", "after": [ { "element": "hello-2", "status": "succeeded" } ] },
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},
	}


def pipeline_failure():
	return {
		"identifier": "pipeline-failure",
		"display_name": "Pipeline Failure",
		"description": "Example pipeline job.",

		"definition": {
			"type": "pipeline",

			"elements": [
				{ "identifier": "hello-before", "job": "hello" },
				{ "identifier": "failure", "job": "failure", "after": [ { "element": "hello-before", "status": "succeeded" } ] },
				{ "identifier": "hello-after", "job": "hello", "after": [ { "element": "failure", "status": "succeeded" } ] },
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},
	}


def pipeline_complex_1():
	return {
		"identifier": "pipeline-complex-1",
		"display_name": "Pipeline Complex 1",
		"description": "Example pipeline job.",

		"definition": {
			"type": "pipeline",

			"elements": [
				{
					"identifier": "stage-1-job-1",
					"job": "hello",
				},

				{
					"identifier": "stage-2-job-1",
					"job": "hello",
					"after": [ { "element": "stage-1-job-1", "status": "succeeded" } ],
				},

				{
					"identifier": "stage-2-job-2",
					"job": "hello",
					"after": [ { "element": "stage-1-job-1", "status": "succeeded" } ],
				},

				{
					"identifier": "stage-2-job-3",
					"job": "hello",
					"after": [ { "element": "stage-1-job-1", "status": "succeeded" } ],
				},

				{
					"identifier": "stage-3-job-1",
					"job": "hello",

					"after": [
						{ "element": "stage-2-job-1", "status": "succeeded" },
						{ "element": "stage-2-job-2", "status": "succeeded" },
						{ "element": "stage-2-job-3", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-3-job-2",
					"job": "hello",

					"after": [
						{ "element": "stage-2-job-1", "status": "succeeded" },
						{ "element": "stage-2-job-2", "status": "succeeded" },
						{ "element": "stage-2-job-3", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-4-job-1",
					"job": "hello",

					"after": [
						{ "element": "stage-1-job-1", "status": "succeeded" },
						{ "element": "stage-3-job-1", "status": "succeeded" },
						{ "element": "stage-3-job-2", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-4-job-2",
					"job": "hello",

					"after": [
						{ "element": "stage-1-job-1", "status": "succeeded" },
						{ "element": "stage-3-job-1", "status": "succeeded" },
						{ "element": "stage-3-job-2", "status": "succeeded" },
					],
				},
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},
	}


def pipeline_complex_2():
	return {
		"identifier": "pipeline-complex-2",
		"display_name": "Pipeline Complex 2",
		"description": "Example pipeline job.",

		"definition": {
			"type": "pipeline",

			"elements": [
				{
					"identifier": "stage-1-job-1",
					"job": "hello",
				},

				{
					"identifier": "stage-1-job-2",
					"job": "hello",
				},

				{
					"identifier": "stage-2-job-1",
					"job": "hello",

					"after": [
						{ "element": "stage-1-job-1", "status": "succeeded" },
						{ "element": "stage-1-job-2", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-2-job-2",
					"job": "hello",

					"after": [
						{ "element": "stage-1-job-1", "status": "succeeded" },
						{ "element": "stage-1-job-2", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-2-job-3",
					"job": "hello",

					"after": [
						{ "element": "stage-1-job-1", "status": "succeeded" },
						{ "element": "stage-1-job-2", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-2-job-4",
					"job": "hello",

					"after": [
						{ "element": "stage-1-job-1", "status": "succeeded" },
						{ "element": "stage-1-job-2", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-3-job-1",
					"job": "hello",

					"after": [
						{ "element": "stage-2-job-1", "status": "succeeded" },
						{ "element": "stage-2-job-2", "status": "succeeded" },
						{ "element": "stage-2-job-3", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-3-job-2",
					"job": "hello",

					"after": [
						{ "element": "stage-2-job-1", "status": "succeeded" },
						{ "element": "stage-2-job-2", "status": "succeeded" },
						{ "element": "stage-2-job-3", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-3-job-3",
					"job": "hello",

					"after": [
						{ "element": "stage-2-job-4", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-4-job-1",
					"job": "hello",

					"after": [
						{ "element": "stage-1-job-1", "status": "succeeded" },
						{ "element": "stage-3-job-1", "status": "succeeded" },
						{ "element": "stage-3-job-2", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-4-job-2",
					"job": "hello",

					"after": [
						{ "element": "stage-1-job-1", "status": "succeeded" },
						{ "element": "stage-2-job-4", "status": "succeeded" },
					],
				},
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},
	}


def pipeline_complex_3():
	return {
		"identifier": "pipeline-complex-3",
		"display_name": "Pipeline Complex 3",
		"description": "Example pipeline job.",

		"definition": {
			"type": "pipeline",

			"elements": [
				{
					"identifier": "stage-1-check",
					"job": "hello",
				},

				{
					"identifier": "stage-2-build-linux",
					"job": "hello",

					"after": [
						{ "element": "stage-1-check", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-2-build-mac",
					"job": "hello",

					"after": [
						{ "element": "stage-1-check", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-2-build-windows",
					"job": "hello",

					"after": [
						{ "element": "stage-1-check", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-3-test-linux",
					"job": "hello",

					"after": [
						{ "element": "stage-2-build-linux", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-3-test-mac",
					"job": "hello",

					"after": [
						{ "element": "stage-2-build-mac", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-3-test-windows",
					"job": "hello",

					"after": [
						{ "element": "stage-2-build-windows", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-4-upload-steam",
					"job": "hello",

					"after": [
						{ "element": "stage-2-build-linux", "status": "succeeded" },
						{ "element": "stage-2-build-mac", "status": "succeeded" },
						{ "element": "stage-2-build-windows", "status": "succeeded" },
						{ "element": "stage-3-test-linux", "status": "succeeded" },
						{ "element": "stage-3-test-mac", "status": "succeeded" },
						{ "element": "stage-3-test-windows", "status": "succeeded" },
					],
				},

				{
					"identifier": "stage-5-release-steam",
					"job": "hello",

					"after": [
						{ "element": "stage-4-upload-steam", "status": "succeeded" },
					],
				},
			],
		},

		"parameters": [],

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},
	}


def configure_schedules():
	return [
		hello_continuous(),
	]


def hello_continuous():
	return {
		"identifier": "hello_continuous",
		"display_name": "Hello Continuous",
		"job": "hello",

		"parameters": {},

		"expression": "* * * * *",
	}
