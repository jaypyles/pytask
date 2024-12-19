from enum import Enum


class SQLDataType(Enum):
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    JSON = "JSON"
    BOOLEAN = "BOOLEAN"
    FLOAT = "FLOAT"
    DATETIME = "DATETIME"


class SQLColumnConditions(Enum):
    NOT_NULL = "NOT NULL"
    NULL = "NULL"
    UNIQUE = "UNIQUE"
    PRIMARY_KEY = "PRIMARY KEY"
    FOREIGN_KEY = "FOREIGN KEY"
    CHECK = "CHECK"
    DEFAULT = "DEFAULT"
