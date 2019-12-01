import bhamon_build_service.run_controller as run_controller
import bhamon_build_service_extensions.project_controller as project_controller
import bhamon_build_service_extensions.run_controller as run_controller_extensions


def configure_overrides():
	run_controller.get_run_results = run_controller_extensions.get_run_results


def register_routes(application):
	application.add_url_rule("/project/<project>/branches", methods = [ "GET" ], view_func = project_controller.get_branch_collection)
	application.add_url_rule("/project/<project>/revisions", methods = [ "GET" ], view_func = project_controller.get_revision_collection)
	application.add_url_rule("/project/<project>/status", methods = [ "GET" ], view_func = project_controller.get_project_status)
