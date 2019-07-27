import logging

import flask
import requests


logger = logging.getLogger("ProjectController")


def get_branch_collection(project):
	access_token = flask.request.args.get("access_token", default = None)
	project_instance = flask.current_app.project_collection[project]
	return flask.jsonify(project_instance.get_branch_list(access_token = access_token))


def get_revision_collection(project):
	query_parameters = {
		"branch": flask.request.args.get("branch", default = None),
		"limit": max(min(flask.request.args.get("limit", default = 20, type = int), 100), 1),
		"access_token": flask.request.args.get("access_token", default = None),
	}

	project_instance = flask.current_app.project_collection[project]
	return flask.jsonify(project_instance.get_revision_list(**query_parameters))


def get_project_status(project):
	branch = flask.request.args.get("branch", default = None)
	access_token = flask.request.args.get("access_token", default = None)
	revision_limit = max(min(flask.request.args.get("revision_limit", default = 20, type = int), 100), 1)
	build_limit = max(min(flask.request.args.get("build_limit", default = 1000, type = int), 10000), 100)

	revision_query_parameters = { "branch": branch, "limit": revision_limit, "access_token": access_token }
	build_query_parameters = { "job": { "$regex": r"^" + project }, "limit": build_limit, "order_by": [("update_date", "descending")] }

	project_instance = flask.current_app.project_collection[project]
	revision_collection = project_instance.get_revision_list(**revision_query_parameters)
	build_collection = flask.current_app.build_provider.get_list_as_documents(**build_query_parameters)

	revision_dictionary = { revision["identifier"]: revision for revision in revision_collection }
	for revision in revision_collection:
		revision["builds"] = []

	for build in build_collection:
		revision_identifier = build.get("results", {}).get("revision_control", {}).get("revision")
		if revision_identifier is None and build["status"] in [ "pending", "running" ]:
			try:
				revision_identifier = project_instance.resolve_revision(build["parameters"]["revision"], access_token = access_token)
			except requests.HTTPError:
				logger.warning("Failed to resolve project '%s' revision '%s'", project, build["parameters"]["revision"], exc_info = True)

		revision = revision_dictionary.get(revision_identifier)
		if revision is not None:
			revision["builds"].append(build)

	return flask.jsonify(revision_collection)
