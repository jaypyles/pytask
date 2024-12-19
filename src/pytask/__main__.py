from pytask.task_queue.task_queue import Queue
from pytask.job.job import Job
from pytask.worker.concurrent_worker import ConcurrentWorker
from pytask.task_queue.types import SQLDataType, SQLColumnConditions
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def func(job: Job):
    logger.info(f"Processing job: {job.task_id}, {job.data}")
    job.data["foo"] += 2


def insert_jobs(queue):
    for i in range(1, 201):
        queue.insert(Job(data={"foo": i, "bar": f"test{i}", "baz": {"foo": "bar"}}))


def main():
    queue = Queue(
        schema=[
            ("foo", SQLDataType.INTEGER, [SQLColumnConditions.NOT_NULL]),
            ("bar", SQLDataType.TEXT, [SQLColumnConditions.NOT_NULL]),
            ("baz", SQLDataType.JSON, [SQLColumnConditions.NOT_NULL]),
        ],
    )

    worker = ConcurrentWorker(queue, func, logger=logger, interval=1, max_workers=16)
    insert_jobs(queue)
    print("Requested Jobs are: ", queue.get_all(search_conditions={"foo": 1}))
    worker.run()


if __name__ == "__main__":
    main()
