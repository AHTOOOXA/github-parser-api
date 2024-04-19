from database import Database
from github_api import GithubAPI


def parse():
    db = Database()
    github_api = GithubAPI()

    params = {
        "q": "stars:>1",
        "sort": "stars",
        "order": "desc",
        "per_page": "5",
    }
    commit_params = {
        "per_page": "20",
    }

    repos = github_api.get_repositories(params)
    repos = db.insert_repositories(repos)

    commits, authors = [], []
    for repo in repos:
        repo_commits, repo_authors = github_api.get_commits_authors_by_repo(repo, commit_params)
        commits.extend(repo_commits)
        authors.extend(repo_authors)

    db.insert_authors(authors)

    author_id_dict = db.get_author_id_dict()
    for commit in commits:
        commit.author_id = author_id_dict[commit.author_name]
    db.insert_commits(commits)
