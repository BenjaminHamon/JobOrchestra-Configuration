import logging

from bhamon_orchestra_master.worker_selector import WorkerSelector as WorkerSelectorBase


logger = logging.getLogger("WorkerSelector")


class WorkerSelector(WorkerSelectorBase):


	def are_compatible(self, worker: dict, job: dict, run: dict) -> bool: # pylint: disable = unused-argument
		""" Check if a worker is able to execute the specified run """

		executors = self._supervisor.get_worker(worker["identifier"]).executors

		try:
			return worker["properties"]["operating_system"] in job["properties"]["operating_system"] \
				and job["properties"]["is_controller"] == worker["properties"]["is_controller"] \
				and len(executors) < worker["properties"]["executor_limit"]

		except KeyError:
			logger.warning("Missing property for matching job and worker", exc_info = True)
			return False
