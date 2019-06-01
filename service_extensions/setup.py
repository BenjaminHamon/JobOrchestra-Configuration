import os
import sys

import setuptools

sys.path.insert(0, os.path.join(sys.path[0], ".."))

import development.configuration # pylint: disable = wrong-import-position
import development.environment # pylint: disable = wrong-import-position


environment_instance = development.environment.load_environment()
configuration_instance = development.configuration.load_configuration(environment_instance)
parameters = development.configuration.get_setuptools_parameters(configuration_instance)


parameters.update({
	"name": "bhamon-build-service-extensions",
	"description": "Extensions for the build service",
	"packages": [ "bhamon_build_service_extensions" ],
	"python_requires": "~= 3.5",
})

setuptools.setup(**parameters)
