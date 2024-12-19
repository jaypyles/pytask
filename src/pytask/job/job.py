from uuid import uuid4
from typing_extensions import override
from typing import Any
from datetime import datetime
import sqlite3
from pytask.job.types import JobStatus


class Job:
    def __init__(
        self,
        task_id: str | None = None,
        status: JobStatus = "pending",
        data: dict[str, Any] = {},
    ):
        self.task_id: str = task_id if task_id is not None else uuid4().hex
        self.status: JobStatus = status
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = datetime.now().isoformat()
        self.data: dict[str, Any] = data

    @override
    def __str__(self):
        return str(self.flat())

    @override
    def __repr__(self):
        return str(self.flat())

    @staticmethod
    def create_from_row(row: sqlite3.Row):
        exclude_keys = {"id", "task_id", "status", "created_at", "updated_at"}
        job = Job()
        job.task_id = row["task_id"]
        job.status = row["status"]
        job.created_at = row["created_at"]
        job.updated_at = row["updated_at"]
        job.data = {key: row[key] for key in row.keys() if key not in exclude_keys}
        return job

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            **self.data,
        }

    def flat(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            **{
                key: value
                for key, value in self.data.items()
                if not key.startswith("_")
            },
        }
