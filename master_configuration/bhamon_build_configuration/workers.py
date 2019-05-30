def configure_workers():
	all_projects = [
		"example",
		"my-website",
	]

	return [
		{
			"identifier": "controller",
			"description": "Build controller",
			"properties": {
				"project": all_projects,
				"operating_system": "windows",
				"is_controller": True,
				"executor_limit": 100,
			},
		},
		{
			"identifier": "worker_01",
			"description": "Build worker",
			"properties": {
				"project": all_projects,
				"operating_system": "windows",
				"is_controller": False,
				"executor_limit": 1,
			},
		},
		{
			"identifier": "worker_02",
			"description": "Build worker",
			"properties": {
				"project": all_projects,
				"operating_system": "windows",
				"is_controller": False,
				"executor_limit": 1,
			},
		},
	]
