controller_script = "bhamon_orchestra_worker_scripts.controller"
initialization_script = "bhamon_orchestra_worker_scripts.example"

worker_configuration_path = "{environment[orchestra_worker_configuration]}"
worker_python_executable = "{environment[orchestra_worker_python_executable]}"


def configure_services(environment_instance): # pylint: disable = unused-argument
	return {}


def configure_jobs():
	return [
		empty(),
		hello(),
		sleep(),
		failure(),
		exception(),
		environment(),
		parameters(),
		large_log(),
		large_log_random(),
		controller_success(),
		controller_failure(),
	]


def empty():
	return {
		"identifier": "example_empty",
		"description": "Example job doing nothing.",
		"workspace": "example",

		"properties": {
			"project": "example",
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],
		"steps": [],
	}


def hello():
	return {
		"identifier": "example_hello",
		"description": "Example job printing hello.",
		"workspace": "example",

		"properties": {
			"project": "example",
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
		"identifier": "example_sleep",
		"description": "Example job sleeping for a few seconds.",
		"workspace": "example",

		"properties": {
			"project": "example",
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
		"identifier": "example_failure",
		"description": "Example job with a failing step.",
		"workspace": "example",

		"properties": {
			"project": "example",
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
		"identifier": "example_exception",
		"description": "Example job with a configuration error.",
		"workspace": "example",

		"properties": {
			"project": "example",
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
	initialization_entry_point = [ worker_python_executable, "-u", "-m", initialization_script ]
	initialization_parameters = [ "--configuration", worker_configuration_path ]

	return {
		"identifier": "example_environment",
		"description": "Example job using environment.",
		"workspace": "example",

		"properties": {
			"project": "example",
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "initialization", "command": initialization_entry_point + initialization_parameters },
		],
	}


def parameters():
	return {
		"identifier": "example_parameters",
		"description": "Example job with parameters.",
		"workspace": "example",

		"properties": {
			"project": "example",
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


def large_log():
	return {
		"identifier": "example_large-log",
		"description": "Example job generating large log files.",
		"workspace": "example",

		"properties": {
			"project": "example",
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
		"identifier": "example_large-log-random",
		"description": "Example job generating large log files with random content.",
		"workspace": "example",

		"properties": {
			"project": "example",
			"operating_system": [ "linux", "windows" ],
			"is_controller": False,
		},

		"parameters": [],

		"steps": [
			{ "name": "write", "command": [ worker_python_executable, "-c", "exec('import uuid\\nfor i in range(1000 * 1000): print(uuid.uuid4())')" ] },
		],
	}


def controller_success():
	controller_entry_point = [ worker_python_executable, "-u", "-m", controller_script ]
	controller_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]

	return {
		"identifier": "example_controller-success",
		"description": "Example controller job.",
		"workspace": "example",

		"properties": {
			"project": "example",
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},

		"parameters": [],

		"steps": [
			{ "name": "trigger_hello", "command": controller_entry_point + controller_parameters + [ "trigger", "example_hello" ] },
			{ "name": "trigger_sleep", "command": controller_entry_point + controller_parameters + [ "trigger", "example_sleep" ] },
			{ "name": "trigger_hello", "command": controller_entry_point + controller_parameters + [ "trigger", "example_hello" ] },
			{ "name": "wait", "command": controller_entry_point + controller_parameters + [ "wait" ] },
		],
	}


def controller_failure():
	controller_entry_point = [ worker_python_executable, "-u", "-m", controller_script ]
	controller_parameters = [ "--configuration", worker_configuration_path, "--results", "{result_file_path}" ]

	return {
		"identifier": "example_controller-failure",
		"description": "Example controller job.",
		"workspace": "example",

		"properties": {
			"project": "example",
			"operating_system": [ "linux", "windows" ],
			"is_controller": True,
		},

		"parameters": [],

		"steps": [
			{ "name": "trigger_hello", "command": controller_entry_point + controller_parameters + [ "trigger", "example_hello" ] },
			{ "name": "trigger_sleep", "command": controller_entry_point + controller_parameters + [ "trigger", "example_sleep" ] },
			{ "name": "trigger_failure", "command": controller_entry_point + controller_parameters + [ "trigger", "example_failure" ] },
			{ "name": "wait", "command": controller_entry_point + controller_parameters + [ "wait" ] },
		],
	}
