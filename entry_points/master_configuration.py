import importlib

import bhamon_build_configuration.projects.example as project_example
import bhamon_build_configuration.projects.my_website as project_my_website
import bhamon_build_configuration.workers as configuration_workers


def reload_modules():
	importlib.reload(project_example)
	importlib.reload(project_my_website)
	importlib.reload(configuration_workers)


def configure():
	all_jobs = []
	all_jobs += project_example.configure_jobs()
	all_jobs += project_my_website.configure_jobs()

	all_workers = configuration_workers.configure_workers()

	return {
		"jobs": all_jobs,
		"workers": all_workers,
	}
