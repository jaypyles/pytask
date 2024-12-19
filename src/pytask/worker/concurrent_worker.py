import threading
from concurrent.futures import ThreadPoolExecutor
from pytask.job import Job
from typing import Callable, Any
from pytask.task_queue import Queue
import logging
from typing_extensions import override

from pytask.worker.base_worker import BaseWorker


class ConcurrentWorker(BaseWorker):
    def __init__(
        self,
        queue: Queue,
        func: Callable[[Job], Any],
        max_workers: int = 5,
        interval: int = 1,
        logger: logging.Logger | None = None,
    ):
        self.queue: Queue = queue
        self.func: Callable[[Job], Any] = func
        self.max_workers: int = max_workers
        self.logger: logging.Logger | None = logger
        self.lock: threading.Lock = threading.Lock()
        self._stop_event: threading.Event = threading.Event()

        super().__init__(queue, func, logger, interval)

    @override
    def run(self) -> None:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while not self._stop_event.is_set():
                job = self.queue.get_oldest_pending()

                if job:
                    with self.lock:

                        _ = executor.submit(self.process_job, job)

                    if self.logger:
                        self.logger.info(f"Job {job.task_id} submitted for processing.")
                else:
                    if self.logger:
                        self.logger.info("No pending jobs found.")

                    _ = threading.Event().wait(1)

    def process_job(self, job: Job) -> None:
        try:
            if self.logger:
                self.logger.info(f"Processing job: {job.task_id}, {job.data}")

            # Process the job
            self.do(job)

            # After processing, update the job status outside the lock
            self.update_job(job)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing job {job.task_id}: {e}")

    def update_job(self, job: Job) -> None:
        with self.lock:
            if self.queue.flags.pop_after_processing:
                _ = self.queue.delete(job.task_id)

                if self.logger:
                    self.logger.info(f"Job {job.task_id} removed from queue.")
            else:
                job.status = "completed"
                self.queue.update(job)

                if self.logger:
                    self.logger.info(f"Job {job.task_id} marked as completed.")

    def stop(self) -> None:
        """Stop the worker cleanly."""
        self._stop_event.set()
