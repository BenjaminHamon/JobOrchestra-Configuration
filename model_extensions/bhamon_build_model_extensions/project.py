import copy

import requests

import bhamon_build_model_extensions.revision_control.github as revision_control_github


class Project:


	def __init__(self, services):
		self.revision_control = services["revision_control"]


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
