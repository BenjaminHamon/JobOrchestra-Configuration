import logging

import flask

import bhamon_build_website.service_client as service_client


logger = logging.getLogger("ProjectController")


def project_index(project_identifier):
	branch = flask.request.args.get("branch", default = None)
	status_limit = max(min(flask.request.args.get("limit", default = 20, type = int), 100), 1)
	access_token = flask.request.args.get("access_token", default = None)
	group_collection = get_status_groups(project_identifier)

	status_parameters = {
		"branch": branch,
		"revision_limit": 20,
		"build_limit": 1000,
		"access_token": access_token,
	}

	project_status = service_client.get("/project/{project_identifier}/status".format(**locals()), status_parameters)
	project_status = [ revision for revision in project_status if len(revision["builds"]) > 0 ][ : status_limit ]

	for revision in project_status:
		for build in revision["builds"]:
			build["group"] = get_build_group(build, group_collection)

	view_data = {
		"project_identifier": project_identifier,
		"project_status": project_status,
		"group_collection": group_collection,
	}

	return flask.render_template("project/index.html", title = "Dashboard", **view_data)


def get_build_group(build, group_collection):
	for group in group_collection:
		if build["job"] == group["job_identifier"] and group.get("condition", lambda build: True)(build):
			return group["identifier"]
	return None


def get_status_groups(project_identifier):
	if project_identifier == "build-service":
		return [
			{
				"identifier": "check",
				"display_name": "Check",
				"job_identifier": "build-service_check",
			},
			{
				"identifier": "distribute",
				"display_name": "Distribution",
				"job_identifier": "build-service_distribute",
			},
		]

	if project_identifier == "image-manager":
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

	if project_identifier == "my-website":
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

	if project_identifier == "solitaire":
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

	raise ValueError("Unknown project: '%s'" % project_identifier)
