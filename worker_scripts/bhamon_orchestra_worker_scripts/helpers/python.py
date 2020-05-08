import logging
import os
import platform
import subprocess


logger = logging.getLogger("Python")


def setup_virtual_environment(python_system_executable):
	logger.info("Setting up python virtual environment")

	setup_venv_command = [ python_system_executable, "-m", "venv", ".venv" ]
	logger.info("+ %s", " ".join(setup_venv_command))
	subprocess.check_call(setup_venv_command)

	if platform.system() == "Linux" and not os.path.exists(".venv/scripts"):
		os.symlink("bin", ".venv/scripts")

	install_pip_command = [ ".venv/scripts/python", "-m", "pip", "install", "--upgrade", "pip" ]
	logger.info("+ %s", " ".join(install_pip_command))
	subprocess.check_call(install_pip_command)
