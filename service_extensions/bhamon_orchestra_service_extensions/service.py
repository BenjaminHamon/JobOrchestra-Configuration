import bhamon_orchestra_service.run_controller as run_controller
import bhamon_orchestra_service_extensions.run_controller as run_controller_extensions


def configure_overrides():
	run_controller.get_results = run_controller_extensions.get_results


def register_routes(application): # pylint: disable = unused-argument
	pass
