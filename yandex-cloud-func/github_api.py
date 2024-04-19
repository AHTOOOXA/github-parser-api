import os
from datetime import datetime

import requests
from models import Author, Commit, Repository


class GithubAPI:
    def __init__(self):
        self.api_token = os.getenv("GITHUB_PAT")
        self.headers = {
            "Authorization": "token %s" % self.api_token,
        }

    def get_repositories(self, params) -> list[Repository]:
        response = requests.get(
            "https://api.github.com/search/repositories", headers=self.headers, params=params, timeout=10,
        )
        data = response.json()
        repositories = []
        for pos, repository in enumerate(data["items"]):
            repo = Repository(
                name=repository["name"],
                owner=repository["owner"]["login"],
                position_cur=pos,
                position_prev=-1,
                stars=repository["stargazers_count"],
                watchers=repository["watchers_count"],
                forks=repository["forks_count"],
                open_issues=repository["open_issues_count"],
                language=repository["language"],
                commits_url=repository["commits_url"][:-6]
            )
            repositories.append(repo)
        return repositories

    def get_commits_authors_by_repo(self, repo: Repository, params) -> (list[Commit], list[Author]):
        response = requests.get(repo.commits_url, headers=self.headers, params=params, timeout=10)
        data = response.json()
        commits = []
        authors = []
        for commit in data:
            sha = commit["sha"]
            date = datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", ""))
            author_name = commit["commit"]["author"]["name"].replace("'", "''")
            author = Author(author_name)
            authors.append(author)
            commit = Commit(sha, repo.repo_id, author_name, date)
            commits.append(commit)
        return commits, authors
