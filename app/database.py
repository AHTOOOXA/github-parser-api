import logging
import os

import asyncpg
from asyncpg import exceptions


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=MetaSingleton):
    def __init__(self):
        self.pool = None  # type: asyncpg.pool.Pool
        self.logger = logging.getLogger("uvicorn.error")  # logger isn't async

    @classmethod
    async def create(cls):
        self = Database()
        await self._create_connection()
        return self

    async def __aenter__(self):
        self.pool = await self._create_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_connection()

    async def _create_connection(self):
        try:
            pool = await asyncpg.create_pool(
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
            self.logger.info("DB INFO")
            self.logger.info(pool)
        except (Exception, exceptions.InterfaceError) as error:
            self.logger.error(f"ERROR PostgreSQL connection {error}")
        else:
            if pool:
                self.logger.info("DB CONNECTION SUCCEEDED\n")
                return pool

    async def _close_connection(self):
        if self.pool:
            await self.pool.close()
            self.logger.info("DB CONNECTION CLOSED")

    async def get_conn(self):
        return await self.pool.acquire()

    async def execute_query(self, query, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)


async def get_db():
    async with Database() as db:
        yield db
