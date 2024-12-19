from pytask.queue import Queue
from pytask.job import Job
from pytask.worker import Worker
from pytask.flags import Flags
from pytask.queue.types import SQLDataType, SQLColumnConditions

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def func(job: Job):
    logger.info(f"Processing job: {job.task_id}, {job.data}")
    job.data["baz"]["foo"] = "bar"


def main():
    flags = Flags(auto_convert_json_keys=True, pop_after_processing=True)
    queue = Queue(
        schema=[
            ("foo", SQLDataType.INTEGER, [SQLColumnConditions.NOT_NULL]),
            ("bar", SQLDataType.TEXT, [SQLColumnConditions.NOT_NULL]),
            ("baz", SQLDataType.JSON, [SQLColumnConditions.NOT_NULL]),
        ],
        flags=flags,
    )
    worker = Worker(queue, func, logger, interval=1)

    queue.insert(Job(data={"foo": 1, "bar": "test", "baz": {"foo": "bar"}}))
    queue.insert(Job(data={"foo": 2, "bar": "test2", "baz": {"foo": "bar"}}))
    queue.insert(Job(data={"foo": 3, "bar": "test3", "baz": {"foo": "bar"}}))

    print("Requested Jobs are: ", queue.get_all(search_conditions={"foo": 1}))

    worker.run()


if __name__ == "__main__":
    main()
