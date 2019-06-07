import bhamon_build_website_extensions.project_controller as project_controller


def register_routes(application):
	application.add_url_rule("/project/<project_identifier>", methods = [ "GET" ], view_func = project_controller.project_index)
