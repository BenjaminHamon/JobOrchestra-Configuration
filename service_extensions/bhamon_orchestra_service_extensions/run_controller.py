import logging

import flask


logger = logging.getLogger("RunController")


def get_run_results(run_identifier):
	run = flask.current_app.run_provider.get(run_identifier)
	run_results = flask.current_app.run_provider.get_results(run_identifier)

	try:
		project = flask.current_app.project_collection[run["job"].split("_")[0]]
		project.update_run_results(run_results)
	except KeyError:
		logger.warning("Failed to resolve artifacts urls for %s %s", run["job"], run["identifier"], exc_info = True)

	return flask.jsonify(run_results)
