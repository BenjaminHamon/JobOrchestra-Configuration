import copy

import requests

import bhamon_build_model_extensions.revision_control.github as revision_control_github


class Project:


	def __init__(self, services):
		self.artifact_repository = services.get("artifact_repository", None)
		self.python_package_repository = services.get("python_package_repository", None)
		self.revision_control = services.get("revision_control", None)


	def get_revision_list(self, branch = None, limit = None, access_token = None):
		if self.revision_control["service"] == "github":
			parameters = copy.deepcopy(self.revision_control["parameters"])
			parameters.update({ "branch": branch, "limit": limit, "access_token": access_token })
			return revision_control_github.get_revision_list(**parameters)

		raise ValueError("Unsupported revision control: '%s'" % self.revision_control["service"])


	def get_revision(self, revision, access_token = None):
		if self.revision_control["service"] == "github":
			parameters = copy.deepcopy(self.revision_control["parameters"])
			parameters.update({ "revision": revision, "access_token": access_token })
			return revision_control_github.get_revision(**parameters)

		raise ValueError("Unsupported revision control: '%s'" % self.revision_control["service"])


	def try_resolve_revision(self, revision, access_token = None):
		if self.revision_control["service"] == "github":
			parameters = copy.deepcopy(self.revision_control["parameters"])
			parameters.update({ "revision": revision, "access_token": access_token })

			try:
				return revision_control_github.get_revision(**parameters)["identifier"]
			except requests.HTTPError:
				return None

		raise ValueError("Unsupported revision control: '%s'" % self.revision_control["service"])


	def update_build_results(self, build_results):
		if self.artifact_repository is not None:
			for artifact in build_results.get("artifacts", []):
				artifact["url"] = self.resolve_artifact_url(artifact)

		if self.python_package_repository is not None:
			for distribution in build_results.get("distributions", []):
				distribution["url"] = self.resolve_python_distribution_url(distribution)


	def resolve_artifact_url(self, artifact):
		artifact_type = self.artifact_repository["file_types"][artifact["type"]]
		return self.artifact_repository["url"] + "/" + artifact_type["path_in_repository"] + "/" + artifact["name"] + artifact_type["file_extension"]


	def resolve_python_distribution_url(self, distribution):
		archive_name = distribution["name"].replace("-", "_") + "-" + distribution["version"]
		return self.python_package_repository["url"] + "/" + distribution["name"] + "/" + archive_name + self.python_package_repository["distribution_extension"]
