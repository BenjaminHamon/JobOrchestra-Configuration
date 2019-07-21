import logging

import flask


logger = logging.getLogger("BuildController")


def get_build_results(build_identifier):
	build = flask.current_app.build_provider.get(build_identifier)
	build_results = flask.current_app.build_provider.get_results(build_identifier)

	try:
		project = flask.current_app.project_collection[build["job"].split("_")[0]]
		project.update_build_results(build_results)
	except KeyError:
		logger.warning("Failed to resolve artifacts urls for %s %s", build["job"], build["identifier"], exc_info = True)

	return flask.jsonify(build_results)
