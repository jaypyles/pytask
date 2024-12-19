from abc import ABC, abstractmethod
from pytask.task_queue.task_queue import Queue
from typing import Callable, Any
from pytask.job.job import Job

import logging

logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    def __init__(
        self,
        queue: Queue,
        func: Callable[[Job], Any],
        logger: logging.Logger | None = None,
        interval: int = 1,
    ):
        self.queue: Queue = queue
        self.func: Callable[[Job], Any] = func
        self.interval: int = interval
        self.logger: logging.Logger | None = logger

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError("Subclass must implement run method")

    def do(self, job: Job):
        self.func(job)
