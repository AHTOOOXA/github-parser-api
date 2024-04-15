# переписать уменьшив количество запросов к базе
# сейчас их 1 + 100 * 100 * 2
# работает вечность РЕАЛЬНО ВЕЧНОСТЬ
import logging
import os
import traceback
from datetime import datetime

import psycopg2
import requests

api_token = os.getenv("GITHUB_PAT")


def _get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
    except Exception as e:
        logging.error(e)
    else:
        if conn:
            return conn
        raise Exception("Failed to connect to the database")


def parse():
    headers = {
        "Authorization": "token %s" % api_token,
    }
    params = {
        "q": "stars:>1",
        "sort": "stars",
        "order": "desc",
        "per_page": "100",
    }
    commit_params = {
        "per_page": "100",
    }
    logger = logging.getLogger()

    conn = _get_db_connection()
    cursor = conn.cursor()

    response = requests.get(
        "https://api.github.com/search/repositories", headers=headers, params=params, timeout=10,
    )
    data = response.json()
    for pos, repository in enumerate(data["items"]):
        try:
            repo = repository["name"]
            owner = repository["owner"]["login"]
            position_cur = pos
            position_prev = -1
            stars = repository["stargazers_count"]
            watchers = repository[
                "watchers_count"]  # for some reason github api returns same number as stargazers_count
            forks = repository["forks_count"]
            open_issues = repository["open_issues_count"]
            language = repository["language"]
            commits_url = repository["commits_url"][:-6]
            cursor.execute("""
                INSERT INTO repositories (repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            """, (repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language))
            repo_id = cursor.fetchone()
            conn.commit()
        except Exception as e:
            logger.error(e, pos, "repo")
        else:
            try:
                commit_response = requests.get(commits_url, headers=headers, params=commit_params, timeout=10)
            except Exception as e:
                logger.error(e, commits_url)
            else:
                commits_response = commit_response.json()
                for commit in commits_response:
                    try:
                        sha = commit["sha"]
                        date = datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", ""))
                        author = commit["commit"]["author"]["name"].replace("'", "''")
                    except Exception:
                        logger.error(traceback.format_exc())
                    else:
                        cursor.execute("""
                        INSERT INTO authors (name)
                        VALUES (%s)
                        ON CONFLICT DO NOTHING
                        """, (author, ))
                        cursor.execute("""
                            SELECT author_id FROM authors WHERE name = %s;
                        """, (author, ))
                        author_id = cursor.fetchone()
                        cursor.execute("""
                            INSERT INTO commits (sha, repo_id, author_id, date)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (sha) DO NOTHING
                            RETURNING commit_id;
                        """, (sha, repo_id[0], author_id[0], date))  # error
                        conn.commit()
    conn.commit()
    conn.close()

