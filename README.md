# pytask

A simple sqlite3-based job queue with a worker. Main purpose is to run jobs in a queue. Jobs are not popped from the queue, which means the queue can act as a history.

## Usage

```python
from pytask import Queue, Worker, Job, SQLDataType, SQLColumnConditions

queue = Queue(schema=[("foo", SQLDataType.INTEGER, [SQLColumnConditions.NOT_NULL])])
worker = Worker(queue, func)

queue.insert(Job(data={"foo": 1, "bar": "test", "baz": {"foo": "bar"}}))
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
