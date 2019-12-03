import bhamon_orchestra_model_extensions.revision_control.github as revision_control_github


class Project:


	def __init__(self, services):
		self.artifact_repository = services.get("artifact_repository", None)
		self.python_package_repository = services.get("python_package_repository", None)
		self.revision_control = services.get("revision_control", None)


	def get_branch_list(self, access_token = None):
		if self.revision_control["service"] == "github":
			parameters = {
				"owner": self.revision_control["owner"],
				"repository": self.revision_control["repository"],
				"access_token": access_token,
			}

			return revision_control_github.get_branch_list(**parameters)

		raise ValueError("Unsupported revision control: '%s'" % self.revision_control["service"])


	def get_revision_list(self, branch = None, limit = None, access_token = None):
		if self.revision_control["service"] == "github":
			parameters = {
				"owner": self.revision_control["owner"],
				"repository": self.revision_control["repository"],
				"branch": branch,
				"limit": limit,
				"access_token": access_token,
			}

			return revision_control_github.get_revision_list(**parameters)

		raise ValueError("Unsupported revision control: '%s'" % self.revision_control["service"])


	def get_revision(self, revision, access_token = None):
		if self.revision_control["service"] == "github":
			parameters = {
				"owner": self.revision_control["owner"],
				"repository": self.revision_control["repository"],
				"revision": revision,
				"access_token": access_token,
			}

			return revision_control_github.get_revision(**parameters)

		raise ValueError("Unsupported revision control: '%s'" % self.revision_control["service"])


	def get_revision_url(self, revision):
		if self.revision_control["service"] == "github":
			parameters = {
				"owner": self.revision_control["owner"],
				"repository": self.revision_control["repository"],
				"revision": revision,
			}

			return revision_control_github.get_revision_url(**parameters)

		raise ValueError("Unsupported revision control: '%s'" % self.revision_control["service"])


	def resolve_revision(self, revision, access_token = None):
		if self.revision_control["service"] == "github":
			parameters = {
				"owner": self.revision_control["owner"],
				"repository": self.revision_control["repository"],
				"revision": revision,
				"access_token": access_token,
			}

			return revision_control_github.get_revision(**parameters)["identifier"]

		raise ValueError("Unsupported revision control: '%s'" % self.revision_control["service"])


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
