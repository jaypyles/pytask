# pytask

A simple sqlite3-based job queue with a worker. Main purpose is to run jobs in a queue. Jobs are not popped from the queue, which means the queue can act as a history.

## Usage

The worker will run the function `func` for each job. The function will be passed a `Job` object. Which means that you can alter the job object in the function, and the newly updated job will be saved to the queue. 

```python
from pytask import Queue, Worker, Job, SQLDataType, SQLColumnConditions

def func(job: Job):
    # Do something with the job
    job.data["foo"] += 1

queue = Queue(schema=[
    ("foo", SQLDataType.INTEGER, [SQLColumnConditions.NOT_NULL]), 
    ("bar", SQLDataType.TEXT, [SQLColumnConditions.NOT_NULL]), 
    ("baz", SQLDataType.JSON, [SQLColumnConditions.NOT_NULL])
])
worker = Worker(queue, func)

queue.insert(Job(data={"foo": 1, "bar": "test", "baz": {"foo": "bar"}}))

worker.run()
```

Creating multiple queues or multiple workers is possible. Creating a new queue object won't actually create a new queue, it just creates a new connection to the queue. Which means you can have multiple queue objects pointing to the same queue, or you can use the same queue object for multiple workers.

Be careful to avoid race conditions when using the same queue object for multiple workers.

## Flags

Flags are used to configure the behavior of the queue and worker.

Current flags:

- `auto_convert_json_keys`: If True, the queue will automatically convert JSON keys to strings. Useful for retrieving and manipulating JSON data.
- `pop_after_processing`: If True, the job will be popped from the queue after processing.

```python
from pytask import Queue, Worker, Job, SQLDataType, SQLColumnConditions, Flags

flags = Flags(auto_convert_json_keys=True, pop_after_processing=True)
queue = Queue(schema=[("foo", SQLDataType.INTEGER, [SQLColumnConditions.NOT_NULL])], flags=flags)

worker = Worker(queue, func, logger=logger)
worker.run()
```

## Concurrent Worker

The concurrent worker is a worker that runs jobs in parallel. It uses a thread pool to run the jobs.

```python
from pytask import Queue, ConcurrentWorker, Job, SQLDataType, SQLColumnConditions

worker = ConcurrentWorker(queue, func, logger=logger, interval=1, max_workers=16)
worker.run()
```
