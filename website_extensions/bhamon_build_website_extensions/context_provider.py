def get_project_default_branch(project):
	if project == "build-service":
		return "master"
	if project == "image-manager":
		return "master"
	if project == "my-website":
		return "master"
	if project == "solitaire":
		return "master"
	raise ValueError("Unknown project: '%s'" % project)


def get_project_context_collection(project):
	if project == "build-service":
		return [ "Summary" ]
	if project == "image-manager":
		return [ "Summary" ]
	if project == "my-website":
		return [ "Summary" ]
	if project == "solitaire":
		return [ "Summary" ]
	raise ValueError("Unknown project: '%s'" % project)


def get_project_context(project, context):
	if project == "build-service":
		return get_build_service_context(context)
	if project == "image-manager":
		return get_image_manager_context(context)
	if project == "my-website":
		return get_my_website_context(context)
	if project == "solitaire":
		return get_solitaire_context(context)
	raise ValueError("Unknown project: '%s'" % project)


def get_build_service_context(context):
	project_filters = get_build_service_filters()

	if context == "Summary":
		return [ f for f in project_filters ]
	raise ValueError("Unknown context '%s' for project '%s'" % (context, "build-service"))


def get_build_service_filters():
	return [
		{
			"identifier": "check_linux",
			"display_name": "Check Linux",
			"job_identifier": "build-service_check_linux",
		},
		{
			"identifier": "check_windows",
			"display_name": "Check Windows",
			"job_identifier": "build-service_check_windows",
		},
		{
			"identifier": "distribute",
			"display_name": "Distribution",
			"job_identifier": "build-service_distribute",
		},
	]


def get_image_manager_context(context):
	project_filters = get_image_manager_filters()

	if context == "Summary":
		return [ f for f in project_filters ]
	raise ValueError("Unknown context '%s' for project '%s'" % (context, "image-manager"))


def get_image_manager_filters():
	return [
		{
			"identifier": "controller",
			"display_name": "Controller",
			"job_identifier": "image-manager_controller",
		},
		{
			"identifier": "package_debug",
			"display_name": "Package (Debug)",
			"job_identifier": "image-manager_package",
			"condition": lambda build: build["parameters"]["configuration"] == "Debug",
		},
		{
			"identifier": "package_release",
			"display_name": "Package (Release)",
			"job_identifier": "image-manager_package",
			"condition": lambda build: build["parameters"]["configuration"] == "Release",
		},
	]


def get_my_website_context(context):
	project_filters = get_my_website_filters()

	if context == "Summary":
		return [ f for f in project_filters ]
	raise ValueError("Unknown context '%s' for project '%s'" % (context, "my-website"))


def get_my_website_filters():
	return [
		{
			"identifier": "check",
			"display_name": "Check",
			"job_identifier": "my-website_check",
		},
		{
			"identifier": "distribute",
			"display_name": "Distribution",
			"job_identifier": "my-website_distribute",
		},
	]


def get_solitaire_context(context):
	project_filters = get_solitaire_filters()

	if context == "Summary":
		return [ f for f in project_filters ]
	raise ValueError("Unknown context '%s' for project '%s'" % (context, "solitaire"))


def get_solitaire_filters():
	return [
		{
			"identifier": "controller",
			"display_name": "Controller",
			"job_identifier": "solitaire_controller",
		},
		{
			"identifier": "package_android_debug",
			"display_name": "Android Package (Debug)",
			"job_identifier": "solitaire_package_android",
			"condition": lambda build: build["parameters"]["configuration"] == "Debug",
		},
		{
			"identifier": "package_android_release",
			"display_name": "Android Package (Release)",
			"job_identifier": "solitaire_package_android",
			"condition": lambda build: build["parameters"]["configuration"] == "Release",
		},
		{
			"identifier": "package_linux_debug",
			"display_name": "Linux Package (Debug)",
			"job_identifier": "solitaire_package_linux",
			"condition": lambda build: build["parameters"]["configuration"] == "Debug",
		},
		{
			"identifier": "package_linux_release",
			"display_name": "Linux Package (Release)",
			"job_identifier": "solitaire_package_linux",
			"condition": lambda build: build["parameters"]["configuration"] == "Release",
		},
		{
			"identifier": "package_windows_debug",
			"display_name": "Windows Package (Debug)",
			"job_identifier": "solitaire_package_windows",
			"condition": lambda build: build["parameters"]["configuration"] == "Debug",
		},
		{
			"identifier": "package_windows_release",
			"display_name": "Windows Package (Release)",
			"job_identifier": "solitaire_package_windows",
			"condition": lambda build: build["parameters"]["configuration"] == "Release",
		},
	]
