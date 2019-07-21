 # pylint: disable = unused-argument

import logging

import requests


logger = logging.getLogger("GitHub")


website_url = "https://github.com"
api_url = "https://api.github.com"


def get_revision_list(owner, repository, branch = None, limit = None, access_token = None):
	url = api_url + "/repos/{owner}/{repository}/commits".format(**locals())
	parameters = { "sha": branch, "per_page": limit }
	parameters = { key: value for key, value in parameters.items() if value is not None }
	headers = { "Authorization": "token %s" % access_token } if access_token is not None else {}
	response = requests.get(url, params = parameters, headers = headers)
	response.raise_for_status()

	revision_list = []
	for item in response.json():
		revision_list.append({
			"identifier": item["sha"],
			"identifier_short": item["sha"][:10],
			"author": item["commit"]["author"]["name"],
			"date": item["commit"]["committer"]["date"],
			"description": item["commit"]["message"],
			"url": item["html_url"],
		})

	return revision_list


def get_revision(owner, repository, revision, access_token = None):
	url = api_url + "/repos/{owner}/{repository}/commits/{revision}".format(**locals())
	headers = { "Authorization": "token %s" % access_token } if access_token is not None else {}
	response = requests.get(url, headers = headers)
	response.raise_for_status()
	revision = response.json()

	return {
		"identifier": revision["sha"],
		"identifier_short": revision["sha"][:10],
		"author": revision["commit"]["author"]["name"],
		"date": revision["commit"]["committer"]["date"],
		"description": revision["commit"]["message"],
		"url": revision["html_url"],
	}


def get_revision_url(owner, repository, revision):
	return website_url + "/{owner}/{repository}/commit/{revision}".format(**locals())
