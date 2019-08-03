import flask

import bhamon_build_website_extensions.project_controller as project_controller


def register_routes(application):
	application.add_url_rule("/artifact_repository", methods = [ "GET" ], view_func = artifact_repository_home)
	application.add_url_rule("/python_package_repository", methods = [ "GET" ], view_func = python_package_repository_home)
	application.add_url_rule("/project/<project_identifier>", methods = [ "GET" ], view_func = project_controller.project_index)


def artifact_repository_home():
	return flask.redirect(flask.current_app.artifact_server_url)


def python_package_repository_home():
	return flask.redirect(flask.current_app.python_package_repository_url)
