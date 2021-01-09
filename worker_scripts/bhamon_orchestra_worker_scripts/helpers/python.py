import configparser
import logging
import os
import platform
import re
import shutil
import subprocess


logger = logging.getLogger("Python")


def setup_virtual_environment(python_system_executable):
	logger.info("Setting up python virtual environment")

	if os.path.exists(".venv"):
		shutil.rmtree(".venv")

	setup_venv_command = [ python_system_executable, "-m", "venv", ".venv" ]
	logger.info("+ %s", " ".join(setup_venv_command))
	subprocess.check_call(setup_venv_command)

	if platform.system() == "Linux" and not os.path.exists(".venv/scripts"):
		os.symlink("bin", ".venv/scripts")

	install_pip_command = [ ".venv/scripts/python", "-m", "pip", "install", "--upgrade", "pip" ]
	logger.info("+ %s", " ".join(install_pip_command))
	subprocess.check_call(install_pip_command)


def configure_unsecure_package_repository(python_package_repository):
	pip_configuration_file_path = ".venv/pip.conf"
	if platform.system() == "Windows":
		pip_configuration_file_path = ".venv/pip.ini"

	http_uri_regex = re.compile(r"^http(s)?://(?P<host>[a-zA-Z0-9\-\.]*)(:(?P<port>[0-9]+))?(?P<path>/[a-zA-Z0-9_\-\./]*)?$")
	python_package_host = re.search(http_uri_regex, python_package_repository).group("host")

	pip_configuration = configparser.ConfigParser()
	pip_configuration["install"] = { "trusted-host": python_package_host }

	with open(pip_configuration_file_path, mode = "w", encoding = "utf-8") as pip_configuration_file:
		pip_configuration.write(pip_configuration_file)
