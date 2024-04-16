import logging
import os
import traceback
from datetime import datetime

import psycopg2
import psycopg2.extras
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

    repos_data = []
    authors_data = []
    commits_data = []
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
            repos_data.append((repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language))
        except Exception as e:
            logger.error(e, pos, "repo")
        else:
            try:
                commit_response = requests.get(commits_url, headers=headers, params=commit_params, timeout=10)
            except Exception as e:
                logger.error(e, commits_url)
            else:
                commits_response = commit_response.json()
                commits_repos_data = []
                for commit in commits_response:
                    try:
                        sha = commit["sha"]
                        date = datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", ""))
                        author = commit["commit"]["author"]["name"].replace("'", "''")
                    except Exception:
                        logger.error(traceback.format_exc())
                    else:
                        authors_data.append((author,))
                        commits_repos_data.append((sha, date, author))
                commits_data.append(commits_repos_data)
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
    """, repos_data)
    repo_ids = cursor.fetchall()
    psycopg2.extras.execute_values(cursor, """
        INSERT INTO authors (name)
        VALUES %s
        ON CONFLICT (name) DO NOTHING
    """, authors_data)

    cursor.execute("SELECT * FROM authors")
    authors = {author[1]: author[0] for author in cursor.fetchall()}

    commits = [(sha, repo_id, authors[author], date)
               for repo_id, repo_commits in zip(repo_ids, commits_data)
               for sha, date, author in repo_commits]

    psycopg2.extras.execute_values(cursor, """
        INSERT INTO commits (sha, repo_id, author_id, date)
        VALUES %s
        ON CONFLICT DO NOTHING
    """, commits)

    conn.commit()
    conn.close()
