import logging


logger = logging.getLogger("RunResultTransformer")


def transform_run_results(project, run_results):
	if run_results is None:
		return None

	if "revision_control" in project["services"]:
		if "revision_control" in run_results:
			run_results["revision_control"]["url"] = _get_revision_url(project, run_results["revision_control"]["revision"])

	for test_run in run_results.get("tests", []):
		test_run["summary_text"] = _generate_test_summary_text(test_run)

	if "artifact_repository" in project["services"]:
		for artifact in run_results.get("artifacts", []):
			artifact["url"] = _resolve_artifact_url(project, artifact)

	if "python_package_repository" in project["services"]:
		for distribution in run_results.get("distributions", []):
			distribution["url"] = _resolve_python_distribution_url(project, distribution)

	return run_results


def _generate_test_summary_text(test_run):
	if test_run['run_type'] == 'pylint':
		return ", ".join("%s: %s" % (key, value) for key, value in test_run["summary"].items() if value > 0)
	if test_run['run_type'] == 'pytest':
		return ", ".join("%s: %s" % (key, value) for key, value in test_run["summary"].items() if value > 0)
	raise ValueError("Unsupported test run type: '%s'" % test_run['run_type'])


def _resolve_artifact_url(project, artifact):
	service = project["services"]["artifact_repository"]
	artifact_type = service["file_types"][artifact["type"]]
	return service["url"] + "/" + artifact_type["path_in_repository"] + "/" + artifact["name"] + artifact_type["file_extension"]


def _resolve_python_distribution_url(project, distribution):
	service = project["services"]["python_package_repository"]
	archive_name = distribution["name"].replace("-", "_") + "-" + distribution["version"]
	return service["url"] + "/" + distribution["name"] + "/" + archive_name + service["distribution_extension"]


def _get_revision_url(project, revision): # pylint: disable = unused-argument
	service = project["services"]["revision_control"]

	if service["type"] == "github":
		repository = service["repository"] # pylint: disable = possibly-unused-variable
		return "https://github.com/{repository}/commit/{revision}".format(**locals())

	raise ValueError("Unsupported service '%s'" % service["type"])
