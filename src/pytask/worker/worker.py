from pytask.queue.queue import Queue
from typing import Callable, Any
from pytask.job import Job
import time

import logging

logger = logging.getLogger(__name__)


class Worker:
    def __init__(
        self,
        queue: Queue,
        func: Callable[[Job], Any],
        logger: logging.Logger | None = None,
        interval: int = 0,
    ):
        self.queue: Queue = queue
        self.func: Callable[[Job], Any] = func
        self.interval: int = interval
        self.logger: logging.Logger | None = logger

    def run(self):
        while True:
            job = self.queue.get_oldest_pending()

            if job:
                if self.logger:
                    self.logger.info(f"Processing job: {job}")

                self.do(job)

                if self.queue.flags.pop_after_processing:
                    _ = self.queue.delete(job.task_id)

                    if self.logger:
                        self.logger.info(f"Job {job.task_id} removed from queue.")
                else:
                    job.status = "completed"
                    self.queue.update(job)

                    if self.logger:
                        self.logger.info(f"Job {job.task_id} marked as completed.")
            else:
                if self.logger:
                    self.logger.info("No pending jobs found.")

            if self.interval > 0:
                time.sleep(self.interval)

    def do(self, job: Job):
        self.func(job)
