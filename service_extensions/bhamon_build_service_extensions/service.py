import bhamon_build_service.build_controller as build_controller
import bhamon_build_service_extensions.build_controller as build_controller_extensions
import bhamon_build_service_extensions.project_controller as project_controller


def configure_overrides():
	build_controller.get_build_results = build_controller_extensions.get_build_results


def register_routes(application):
	application.add_url_rule("/project/<project>/branches", methods = [ "GET" ], view_func = project_controller.get_branch_collection)
	application.add_url_rule("/project/<project>/revisions", methods = [ "GET" ], view_func = project_controller.get_revision_collection)
	application.add_url_rule("/project/<project>/status", methods = [ "GET" ], view_func = project_controller.get_project_status)
