import datetime
import logging
import subprocess

import bhamon_orchestra_worker.workspace


logger = logging.getLogger("Git")


def initialize(environment, repository):
	logger.info("Initializating repository")

	init_command = [ environment["git_executable"], "init" ]
	logger.info("+ %s", " ".join(init_command))
	subprocess.check_call(init_command)

	add_remote_command = [ environment["git_executable"], "remote", "add", "origin", repository ]
	logger.info("+ %s", " ".join(add_remote_command))
	subprocess.call(add_remote_command)

	set_remote_command = [ environment["git_executable"], "remote", "set-url", "origin", repository ]
	logger.info("+ %s", " ".join(set_remote_command))
	subprocess.check_call(set_remote_command)


def resolve(environment, revision):
	try:
		revision_command = [ environment["git_executable"], "rev-parse", "--verify", "origin/" + revision ]
		logger.info("+ %s", " ".join(revision_command))
		return subprocess.check_output(revision_command).decode("utf-8").strip()
	except subprocess.CalledProcessError:
		pass

	try:
		revision_command = [ environment["git_executable"], "rev-parse", "--verify", revision ]
		logger.info("+ %s", " ".join(revision_command))
		return subprocess.check_output(revision_command).decode("utf-8").strip()
	except subprocess.CalledProcessError:
		pass

	raise ValueError("Could not resolve exact revision for '%s'" % revision)


def update(environment, revision, result_file_path):
	logger.info("Updating to revision '%s'", revision)

	fetch_command = [ environment["git_executable"], "fetch", "--verbose" ]
	logger.info("+ %s", " ".join(fetch_command))
	subprocess.check_call(fetch_command)

	revision_exact = resolve(environment, revision)

	date_command = [ environment["git_executable"], "show", "--no-patch", "--format=%ct", revision_exact ]
	logger.info("+ %s", " ".join(date_command))
	revision_date = int(subprocess.check_output(date_command).decode("utf-8").strip())
	revision_date = datetime.datetime.utcfromtimestamp(revision_date).replace(microsecond = 0).isoformat() + "Z"

	results = bhamon_orchestra_worker.workspace.load_results(result_file_path)
	results["revision_control"] = { "revision": revision_exact, "date": revision_date }
	bhamon_orchestra_worker.workspace.save_results(result_file_path, results)

	logger.info("Revision: '%s' (%s)", revision_exact, revision_date)

	checkout_command = [ environment["git_executable"], "-c", "advice.detachedHead=false", "checkout", revision_exact ]
	logger.info("+ %s", " ".join(checkout_command))
	subprocess.check_call(checkout_command)
