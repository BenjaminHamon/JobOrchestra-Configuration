import bhamon_build_service_extensions.project_controller as project_controller


def register_routes(application):
	application.add_url_rule("/project/<project>/revisions", methods = [ "GET" ], view_func = project_controller.get_revision_collection)
	application.add_url_rule("/project/<project>/status", methods = [ "GET" ], view_func = project_controller.get_project_status)
