import os
from enum import Enum


class Database(Enum):
    telegramcms = "postgres://{}:{}@{}:{}/{}".format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PASS"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
        os.environ.get("DB_NAME")
    )
