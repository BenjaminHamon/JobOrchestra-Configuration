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
	"name": "bhamon-orchestra-configuration",
	"description": "Configuration for the Job Orchestra master",

	"packages": [
		"bhamon_orchestra_configuration",
		"bhamon_orchestra_configuration/projects",
	],

	"python_requires": "~= 3.5",
})

setuptools.setup(**parameters)
