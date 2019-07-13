def configure_workers():
	return configure_linux_workers() + configure_windows_workers()


def configure_linux_workers():
	all_projects = [
		"build-service",
		"example",
		"image-manager",
		"my-website",
		"solitaire",
	]

	return [
		{
			"identifier": "linux_controller",
			"description": "Build controller",
			"properties": {
				"project": all_projects,
				"operating_system": "linux",
				"is_controller": True,
				"executor_limit": 100,
			},
		},
		{
			"identifier": "linux_worker_01",
			"description": "Build worker",
			"properties": {
				"project": all_projects,
				"operating_system": "linux",
				"is_controller": False,
				"executor_limit": 1,
			},
		},
		{
			"identifier": "linux_worker_02",
			"description": "Build worker",
			"properties": {
				"project": all_projects,
				"operating_system": "linux",
				"is_controller": False,
				"executor_limit": 1,
			},
		},
	]


def configure_windows_workers():
	all_projects = [
		"build-service",
		"example",
		"image-manager",
		"my-website",
		"solitaire",
	]

	return [
		{
			"identifier": "windows_controller",
			"description": "Build controller",
			"properties": {
				"project": all_projects,
				"operating_system": "windows",
				"is_controller": True,
				"executor_limit": 100,
			},
		},
		{
			"identifier": "windows_worker_01",
			"description": "Build worker",
			"properties": {
				"project": all_projects,
				"operating_system": "windows",
				"is_controller": False,
				"executor_limit": 1,
			},
		},
		{
			"identifier": "windows_worker_02",
			"description": "Build worker",
			"properties": {
				"project": all_projects,
				"operating_system": "windows",
				"is_controller": False,
				"executor_limit": 1,
			},
		},
	]
