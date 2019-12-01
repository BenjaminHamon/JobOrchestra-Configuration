import logging

import flask

import bhamon_build_website.service_client as service_client
import bhamon_build_website_extensions.context_provider as context_provider


logger = logging.getLogger("ProjectController")


def project_index(project_identifier):
	project_branch = flask.request.args.get("branch", default = None)
	context_identifier = flask.request.args.get("context", default = None)
	status_limit = max(min(flask.request.args.get("limit", default = 20, type = int), 100), 1)
	access_token = flask.request.args.get("access_token", default = None)

	project_branch_collection = service_client.get("/project/{project_identifier}/branches".format(**locals()), { "access_token": access_token })
	project_context_collection = context_provider.get_project_context_collection(project_identifier)

	if project_branch is None:
		project_branch = context_provider.get_project_default_branch(project_identifier)
	if context_identifier is None:
		context_identifier = project_context_collection[0]
	project_context = context_provider.get_project_context(project_identifier, context_identifier)

	status_parameters = {
		"branch": project_branch,
		"revision_limit": 20,
		"build_limit": 1000,
		"access_token": access_token,
	}

	project_status = service_client.get("/project/{project_identifier}/status".format(**locals()), status_parameters)
	project_status = [ revision for revision in project_status if len(revision["builds"]) > 0 ][ : status_limit ]

	for revision in project_status:
		revision["builds_by_filter"] = { f["identifier"]: [] for f in project_context }
		for build in revision["builds"]:
			for build_filter in project_context:
				if build["job"] == build_filter["job_identifier"] and build_filter.get("condition", lambda build: True)(build):
					revision["builds_by_filter"][build_filter["identifier"]].append(build)

	view_data = {
		"project_identifier": project_identifier,
		"project_branch": project_branch,
		"project_branch_collection": project_branch_collection,
		"project_context_identifier": context_identifier,
		"project_context": project_context,
		"project_context_collection": project_context_collection,
		"project_status": project_status,
	}

	return flask.render_template("project/index.html", title = "Dashboard", **view_data)
