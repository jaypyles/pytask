from pytask.task_queue.task_queue import Queue
from typing import Callable, Any
from pytask.job import Job
import time
from collections.abc import Coroutine

import logging

logger = logging.getLogger(__name__)


class AsyncWorker:
    def __init__(
        self,
        queue: Queue,
        func: Callable[[Job], Coroutine[Any, Any, Any]],
        logger: logging.Logger | None = None,
        interval: int = 1,
    ):
        self.queue: Queue = queue
        self.func: Callable[[Job], Coroutine[Any, Any, Any]] = func
        self.interval: int = interval
        self.logger: logging.Logger | None = logger

    async def run(self):
        while True:
            job = self.queue.get_oldest_pending()

            if job:
                if self.logger:
                    self.logger.info(f"Processing job: {job}")

                await self.do(job)

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

    async def do(self, job: Job):
        await self.func(job)
