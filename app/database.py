# REWRITE WITH ASYNCPG
# REWRITE WITH ASYNCPG
# REWRITE WITH ASYNCPG
import psycopg2
import psycopg2.extras
from psycopg2 import Error
import os


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=MetaSingleton):
    def __init__(self):
        print("database init works")
        self.conn = None  # type: psycopg2.connection
        self.cur = None  # type: psycopg2.cursor
        self._create_connection()

    def __del__(self):
        self._close_connection()

    def _create_connection(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
            self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            print("DB INFO")
            print(self.conn.get_dsn_parameters(), "\n")
        except (Exception, Error) as error:
            print("ERROR PostgreSQL connection", error)
        finally:
            if self.conn:
                print("DB CONNECTION SUCCEEDED\n")

    def _close_connection(self):
        if self.conn:
            self.conn.commit()
            self.cur.close()
            self.conn.close()
            print("DB CONNECTION CLOSED")

    def get_cur(self):
        return self.cur


def get_db() -> Database:
    return Database()
