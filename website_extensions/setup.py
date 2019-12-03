import os
import sys

import setuptools

sys.path.insert(0, os.path.join(sys.path[0], ".."))

import development.configuration # pylint: disable = wrong-import-position
import development.environment # pylint: disable = wrong-import-position


environment_instance = development.environment.load_environment()
configuration_instance = development.configuration.load_configuration(environment_instance)
parameters = development.configuration.get_setuptools_parameters(configuration_instance)


resource_patterns = [ 'static/**/*.css', 'static/**/*.js', 'templates/**/*.html' ]

parameters.update({
	"name": "bhamon-orchestra-website-extensions",
	"description": "Extensions for the website component of Job Orchestra",
	"packages": [ "bhamon_orchestra_website_extensions" ],
	"python_requires": "~= 3.5",
	"install_requires": [ "flask ~= 1.0", "requests ~= 2.21" ],
	"package_data": { "bhamon_orchestra_website_extensions": development.configuration.list_package_data("bhamon_orchestra_website_extensions", resource_patterns) },
})

setuptools.setup(**parameters)
