controller_script = "bhamon_orchestra_worker_scripts.controller"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_project():
	return {
		"identifier": "example",
		"display_name": "Example",
		"jobs": configure_jobs(),
		"schedules": configure_schedules(),
		"services": [],
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
	]


def empty():
	return {
		"identifier": "empty",
		"display_name": "Empty",
		"description": "Example job doing nothing.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],
		"steps": [],
	}


def hello():
	return {
		"identifier": "hello",
		"display_name": "Hello",
		"description": "Example job printing hello.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
			{ "name": "hello_stderr", "command": [ worker_python_executable, "-c", "import sys; print('hello from stderr', file = sys.stderr)" ] },
		],
	}


def sleep():
	return {
		"identifier": "sleep",
		"display_name": "Sleep",
		"description": "Example job sleeping for a few seconds.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
			{ "name": "sleep", "command": [ worker_python_executable, "-c", "import time; time.sleep(60)" ] },
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
		],
	}


def failure():
	return {
		"identifier": "failure",
		"display_name": "Failure",
		"description": "Example job with a failing step.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
			{ "name": "fail", "command": [ worker_python_executable, "-c", "raise RuntimeError" ] },
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
		],
	}


def exception():
	return {
		"identifier": "exception",
		"display_name": "Exception",
		"description": "Example job with a configuration error.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
			{ "name": "exception", "command": [ worker_python_executable, "-c", "print('{undefined}')" ] },
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('hello')" ] },
		],
	}


def environment():
	script = "bhamon_orchestra_worker_scripts.examples.environment"
	command = [ worker_python_executable, "-u", "-m", script ]
	command_parameters = [ "--configuration", worker_configuration_path ]

	return {
		"identifier": "environment",
		"display_name": "Environment",
		"description": "Example job using environment.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "initialization", "command": command + command_parameters },
		],
	}


def parameters():
	return {
		"identifier": "parameters",
		"display_name": "Parameters",
		"description": "Example job with parameters.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [
			{ "key": "text_to_print", "description": "Text to write to log" },
		],

		"steps": [
			{ "name": "hello", "command": [ worker_python_executable, "-c", "print('{parameters[text_to_print]}')" ] },
		],
	}


def log_with_special_characters():
	return {
		"identifier": "log-with-special-characters",
		"display_name": "Log with Special Characters",
		"description": "Example job generating log files containing special characters.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "write", "command": [ worker_python_executable, "-c", "print('… é ² √ 👍')" ] },
		],
	}


def log_with_html():
	return {
		"identifier": "log-with-html",
		"display_name": "Log with HTML",
		"description": "Example job generating log files containing html.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "write", "command": [ worker_python_executable, "-c", "print('<p>hello</p>')" ] },
		],
	}


def large_log():
	return {
		"identifier": "large-log",
		"display_name": "Large Log",
		"description": "Example job generating large log files.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "write", "command": [ worker_python_executable, "-c", "for i in range(1000 * 1000): print('Testing for large log files')" ] },
		],
	}


def large_log_random():
	return {
		"identifier": "large-log-random",
		"display_name": "Large Log Random",
		"description": "Example job generating large log files with random content.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "write", "command": [ worker_python_executable, "-c", "exec('import uuid\\nfor i in range(1000 * 1000): print(uuid.uuid4())')" ] },
		],
	}


def slow_log():
	return {
		"identifier": "slow_log",
		"display_name": "Slow Log",
		"description": "Example job generating a log over some time.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "initialization", "command": [ worker_python_executable, "-u", "-m", "bhamon_orchestra_worker_scripts.examples.slow_log" ] },
		],
	}


def controller_success():
	controller_entry_point = [ worker_python_executable, "-u", "-m", controller_script ]
	controller_entry_point += [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	trigger_source_parameters = [ "--source-project", "{project_identifier}", "--source-run", "{run_identifier}" ]

	return {
		"identifier": "controller-success",
		"display_name": "Controller Success",
		"description": "Example controller job.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},

		"parameters": [],

		"steps": [
			{ "name": "trigger_hello", "command": controller_entry_point + [ "trigger", "--project", "example", "--job", "hello" ] + trigger_source_parameters },
			{ "name": "trigger_sleep", "command": controller_entry_point + [ "trigger", "--project", "example", "--job", "sleep" ] + trigger_source_parameters },
			{ "name": "trigger_hello", "command": controller_entry_point + [ "trigger", "--project", "example", "--job", "hello" ] + trigger_source_parameters },
			{ "name": "wait", "command": controller_entry_point + [ "wait" ] },
		],
	}


def controller_failure():
	controller_entry_point = [ worker_python_executable, "-u", "-m", controller_script ]
	controller_entry_point += [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]
	trigger_source_parameters = [ "--source-project", "{project_identifier}", "--source-run", "{run_identifier}" ]

	return {
		"identifier": "controller-failure",
		"display_name": "Controller Failure",
		"description": "Example controller job.",
		"workspace": "example",

		"properties": {
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},

		"parameters": [],

		"steps": [
			{ "name": "trigger_hello", "command": controller_entry_point + [ "trigger", "--project", "example", "--job", "hello" ] + trigger_source_parameters },
			{ "name": "trigger_sleep", "command": controller_entry_point + [ "trigger", "--project", "example", "--job", "sleep" ] + trigger_source_parameters },
			{ "name": "trigger_failure", "command": controller_entry_point + [ "trigger", "--project", "example", "--job", "failure" ] + trigger_source_parameters },
			{ "name": "wait", "command": controller_entry_point + [ "wait" ] },
		],
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
