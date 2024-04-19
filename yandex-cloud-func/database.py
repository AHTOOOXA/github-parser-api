import os
import psycopg2
import psycopg2.extras
import logging

from typing import List
from models import Repository, Author, Commit


class Database:
    def __init__(self):
        self.conn = self._get_db_connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_connection()

    def _get_db_connection(self):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
            conn.set_session(autocommit=True)
        except Exception as e:
            logging.error(e)
        else:
            if conn:
                return conn
            raise Exception("Failed to connect to the database")

    def _close_connection(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def insert_repositories(self, repos: List[Repository]) -> List[Repository]:
        with self.conn.cursor() as cursor:
            psycopg2.extras.execute_values(cursor, """
                INSERT INTO repositories (repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language)
                VALUES %s
                ON CONFLICT (repo) DO UPDATE
                SET
                    position_prev = repositories.position_cur,
                    position_cur = EXCLUDED.position_cur,
                    stars = EXCLUDED.stars,
                    watchers = EXCLUDED.watchers,
                    forks = EXCLUDED.forks,
                    open_issues = EXCLUDED.open_issues,
                    language = EXCLUDED.language
                RETURNING repo_id;
            """, (repo.to_db() for repo in repos))
            ids = cursor.fetchall()
            for repo_id, repo in zip(ids, repos):
                repo.repo_id = repo_id[0]
            return repos

    def insert_authors(self, authors: List[Author]):
        with self.conn.cursor() as cursor:
            psycopg2.extras.execute_values(cursor, """
                INSERT INTO authors (name)
                VALUES %s
                ON CONFLICT (name) DO NOTHING
            """, (author.to_db() for author in authors))

    def get_author_id_dict(self) -> dict[str, int]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM authors")
            return {author[1]: author[0] for author in cursor.fetchall()}

    def insert_commits(self, commits: List[Commit]):
        with self.conn.cursor() as cursor:
            psycopg2.extras.execute_values(cursor, """
                INSERT INTO commits (sha, repo_id, author_id, date)
                VALUES %s
                ON CONFLICT DO NOTHING
            """, (commit.to_db() for commit in commits))
