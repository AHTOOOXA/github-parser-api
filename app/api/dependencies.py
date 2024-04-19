from app.services.github_service import GithubService
from app.database.database import Database


def github_service():
    return GithubService(Database())
