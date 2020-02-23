import importlib

import bhamon_orchestra_configuration.projects.development_toolkit as project_development_toolkit
import bhamon_orchestra_configuration.projects.example as project_example
import bhamon_orchestra_configuration.projects.image_manager as project_image_manager
import bhamon_orchestra_configuration.projects.job_orchestra as project_job_orchestra
import bhamon_orchestra_configuration.projects.job_orchestra_configuration as project_job_orchestra_configuration
import bhamon_orchestra_configuration.projects.my_website as project_my_website
import bhamon_orchestra_configuration.projects.solitaire as project_solitaire
import bhamon_orchestra_configuration.worker_selector as worker_selector


def reload_modules():
	importlib.reload(project_development_toolkit)
	importlib.reload(project_example)
	importlib.reload(project_image_manager)
	importlib.reload(project_job_orchestra)
	importlib.reload(project_job_orchestra_configuration)
	importlib.reload(project_my_website)
	importlib.reload(project_solitaire)
	importlib.reload(worker_selector)


def configure(environment):
	all_projects = [
		project_development_toolkit.configure_project(environment),
		project_example.configure_project(),
		project_image_manager.configure_project(environment),
		project_job_orchestra_configuration.configure_project(environment),
		project_job_orchestra.configure_project(environment),
		project_my_website.configure_project(environment),
		project_solitaire.configure_project(environment),
	]

	return {
		"projects": all_projects,
	}
