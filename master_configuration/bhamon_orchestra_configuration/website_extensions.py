import flask


def register_routes(application):
	application.add_url_rule("/artifact_repository", methods = [ "GET" ], view_func = artifact_repository_home)
	application.add_url_rule("/python_package_repository", methods = [ "GET" ], view_func = python_package_repository_home)


def artifact_repository_home():
	return flask.redirect(flask.current_app.artifact_server_url)


def python_package_repository_home():
	return flask.redirect(flask.current_app.python_package_repository_url)
