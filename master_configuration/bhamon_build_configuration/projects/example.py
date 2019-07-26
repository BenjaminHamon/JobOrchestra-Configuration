def configure_services(environment_instance): # pylint: disable = unused-argument
	return {}


def configure_jobs():
	return [
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
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
			{ "name": "hello_stderr", "command": [ "{environment[build_worker_python_executable]}", "-c", "import sys; print('hello from stderr', file = sys.stderr)" ] },
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
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
			{ "name": "sleep", "command": [ "{environment[build_worker_python_executable]}", "-c", "import time; time.sleep(60)" ] },
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
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
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
			{ "name": "fail", "command": [ "{environment[build_worker_python_executable]}", "-c", "raise RuntimeError" ] },
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
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
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
			{ "name": "exception", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('{undefined}')" ] },
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('hello')" ] },
		],
	}


def environment():
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
			{ "name": "configuration", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('{environment[build_worker_configuration]}')" ] },
			{ "name": "python_executable", "command": [ "{environment[build_worker_python_executable]}", "-c", "import sys; print(sys.executable)" ] },
			{ "name": "script_root", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('{environment[build_worker_script_root]}')" ] },
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
			{ "name": "hello", "command": [ "{environment[build_worker_python_executable]}", "-c", "print('{parameters[text_to_print]}')" ] },
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
			{ "name": "write", "command": [ "{environment[build_worker_python_executable]}", "-c", "for i in range(1000 * 1000): print('Testing for large log files')" ] },
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
			{ "name": "write", "command": [ "{environment[build_worker_python_executable]}", "-c", "exec('import uuid\\nfor i in range(1000 * 1000): print(uuid.uuid4())')" ] },
		],
	}


def controller_success():
	controller_script = [ "{environment[build_worker_python_executable]}", "-u", "{environment[build_worker_script_root]}/controller.py" ]
	controller_script += [ "--configuration", "{environment[build_worker_configuration]}", "--results", "{result_file_path}" ]

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
			{ "name": "trigger_hello", "command": controller_script + [ "trigger", "example_hello" ] },
			{ "name": "trigger_sleep", "command": controller_script + [ "trigger", "example_sleep" ] },
			{ "name": "trigger_hello", "command": controller_script + [ "trigger", "example_hello" ] },
			{ "name": "wait", "command": controller_script + [ "wait" ] },
		],
	}


def controller_failure():
	controller_script = [ "{environment[build_worker_python_executable]}", "-u", "{environment[build_worker_script_root]}/controller.py" ]
	controller_script += [ "--configuration", "{environment[build_worker_configuration]}", "--results", "{result_file_path}" ]

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
			{ "name": "trigger_hello", "command": controller_script + [ "trigger", "example_hello" ] },
			{ "name": "trigger_sleep", "command": controller_script + [ "trigger", "example_sleep" ] },
			{ "name": "trigger_failure", "command": controller_script + [ "trigger", "example_failure" ] },
			{ "name": "wait", "command": controller_script + [ "wait" ] },
		],
	}
