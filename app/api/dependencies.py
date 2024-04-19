from app.database.database import Database
from app.services.github_service import GithubService


def github_service():
    return GithubService(Database())
