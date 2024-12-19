import os
import sqlite3
from typing import Any

from pytask.task_queue.constants import BASE_SCHEMA, DEFAULT_PATH
from pytask.job.job import Job
from pytask.task_queue.types import SQLDataType, SQLColumnConditions
import json

from pytask.flags import Flags


class Queue:
    """
    A queue is a collection of jobs that are waiting to be processed. Using the default path,
    the queue will be stored in the current working directory, under ./data/queue.db.

    The queue is stored in a SQLite database, and the table is named "job". Creating more than one object will result in accessing the same queue, unless the path is changed.

    Parameters
    ----------
    schema : list[tuple[str, SQLDataType, list[SQLColumnConditions]]]
        The schema of the queue.
    path : str
        The path to the SQLite database. Defaults to ./data/queue.db.
    flags : Flags
        The flags to configure the behavior of the queue.
    """

    def __init__(
        self,
        schema: list[tuple[str, SQLDataType, list[SQLColumnConditions]]] = [],
        path: str = DEFAULT_PATH,
        flags: Flags = Flags(),
    ):
        self.schema: list[tuple[str, SQLDataType, list[SQLColumnConditions]]] = schema
        self.path: str = path
        self.base_schema: str = BASE_SCHEMA
        self.sql_schema: str = self.__create_sql_schema()
        self.insert_schema: str = self.__create_insert_schema()
        self.json_keys: list[str] = self.__get_json_keys()
        self.flags: Flags = flags
        _ = self.__create_table()

    def insert(self, job: Job):
        with sqlite3.connect(self.path) as conn:
            if self.flags.auto_convert_json_keys:
                self.__dump_json_keys(job)

            _ = conn.execute(self.insert_schema, job.to_dict())

    def update(self, job: Job):
        update_schema = self.__create_update_schema(job.data)

        if self.flags.auto_convert_json_keys:
            self.__dump_json_keys(job)

        with sqlite3.connect(self.path) as conn:
            _ = conn.execute(update_schema, job.to_dict())

    def delete(self, task_id: str):
        with sqlite3.connect(self.path) as conn:
            _ = conn.execute("DELETE FROM job WHERE task_id = ?", (task_id,))

        return True

    def get(self, task_id: str) -> Job | None:
        with self.__connect() as conn:
            cursor = conn.execute("SELECT * FROM job WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()

            if row:
                return Job.create_from_row(row)

            return None

    def get_all(self, search_conditions: dict[str, Any] = {}) -> list[Job]:
        """
        Get all jobs that match the search conditions.

        Parameters
        ----------
        search_conditions : dict[str, Any]
            The conditions to search for. Currently only supports equality such as foo = 1, where search_conditions = {"foo": 1}.
        """
        conditions_str = " AND ".join([f"{key} = :{key}" for key in search_conditions])
        where_clause = f"WHERE {conditions_str}" if conditions_str else ""

        with self.__connect() as conn:
            cursor = conn.execute(
                f"SELECT * FROM job {where_clause}",
                search_conditions,
            )

            rows = cursor.fetchall()
            jobs = [Job.create_from_row(row) for row in rows]

            if self.flags.auto_convert_json_keys:
                for job in jobs:
                    self.__load_json_keys(job)

            return jobs

    def get_oldest_pending(self) -> Job | None:
        with self.__connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM job WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1"
            )
            row = cursor.fetchone()

            if row:
                job = Job.create_from_row(row)

                job.status = "running"
                self.update(job)

                if self.flags.auto_convert_json_keys:
                    self.__load_json_keys(job)

                return job

            return None

    def __connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def __create_sql_schema(self) -> str:
        schema_parts: list[str] = []
        for column in self.schema:
            column_name, column_type, column_conditions = column
            schema_parts.append(
                f"{column_name} {column_type.value} {' '.join([condition.value for condition in column_conditions])}"
            )

        schema = ", ".join(schema_parts)
        job_schema = self.base_schema

        if schema:
            job_schema += f", {schema}"

        return f"""CREATE TABLE IF NOT EXISTS job (       
            {job_schema}
        )"""

    def __create_table(self):
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

        try:
            with sqlite3.connect(self.path) as conn:
                _ = conn.execute(self.sql_schema)
        except Exception:
            return False

        return True

    def __create_insert_schema(self) -> str:
        other_columns: list[str] = []

        for column in self.schema:
            column_name, _, _ = column
            other_columns.append(column_name)

        other_columns_str = ", ".join(other_columns)
        other_columns_values = ", ".join([f":{col}" for col in other_columns])

        return f"""
        INSERT INTO job (task_id, status, created_at, updated_at, {other_columns_str}) 
        VALUES (:task_id, :status, :created_at, :updated_at, {other_columns_values});
        """

    def __create_update_schema(self, extra_columns: dict[str, Any] = {}) -> str:
        extra_columns_str = ", ".join([f"{col} = :{col}" for col in extra_columns])

        return f"""
        UPDATE job SET 
            status = :status, 
            updated_at = :updated_at{f", {extra_columns_str}" if extra_columns_str else ""}
        WHERE task_id = :task_id;
        """

    def __load_json_keys(self, job: Job):
        for key in self.json_keys:
            job.data[key] = json.loads(job.data[key])

    def __dump_json_keys(self, job: Job):
        for key in self.json_keys:
            if not isinstance(job.data[key], str):
                job.data[key] = json.dumps(job.data[key])

    def __get_json_keys(self) -> list[str]:
        json_keys: list[str] = []

        for column in self.schema:
            column_name, column_type, _ = column

            if column_type == SQLDataType.JSON:
                json_keys.append(column_name)

        return json_keys
