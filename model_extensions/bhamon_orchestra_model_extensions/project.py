class Project:


	def __init__(self, services):
		self.artifact_repository = services.get("artifact_repository", None)
		self.python_package_repository = services.get("python_package_repository", None)
		self.revision_control = services.get("revision_control", None)


	def update_run_results(self, run_results):
		if self.revision_control is not None:
			if "revision_control" in run_results:
				run_results["revision_control"]["url"] = self.get_revision_url(run_results["revision_control"]["revision"])

		for test_run in run_results.get("tests", []):
			test_run["summary_text"] = self.generate_test_summary_text(test_run)

		if self.artifact_repository is not None:
			for artifact in run_results.get("artifacts", []):
				artifact["url"] = self.resolve_artifact_url(artifact)

		if self.python_package_repository is not None:
			for distribution in run_results.get("distributions", []):
				distribution["url"] = self.resolve_python_distribution_url(distribution)


	def generate_test_summary_text(self, test_run): # pylint: disable = no-self-use
		if test_run['run_type'] == 'pylint':
			return ", ".join("%s: %s" % (key, value) for key, value in test_run["summary"].items() if value > 0)
		if test_run['run_type'] == 'pytest':
			return ", ".join("%s: %s" % (key, value) for key, value in test_run["summary"].items() if value > 0)
		raise ValueError("Unsupported test run type: '%s'" % test_run['run_type'])


	def resolve_artifact_url(self, artifact):
		artifact_type = self.artifact_repository["file_types"][artifact["type"]]
		return self.artifact_repository["url"] + "/" + artifact_type["path_in_repository"] + "/" + artifact["name"] + artifact_type["file_extension"]


	def resolve_python_distribution_url(self, distribution):
		archive_name = distribution["name"].replace("-", "_") + "-" + distribution["version"]
		return self.python_package_repository["url"] + "/" + distribution["name"] + "/" + archive_name + self.python_package_repository["distribution_extension"]


	def get_revision_url(self, revision): # pylint: disable = unused-argument
		if self.revision_control["type"] == "github":
			repository = self.revision_control["repository"] # pylint: disable = possibly-unused-variable
			return "https://github.com/{repository}/commit/{revision}".format(**locals())

		raise ValueError("Unsupported service '%s'" % self.revision_control["type"])
