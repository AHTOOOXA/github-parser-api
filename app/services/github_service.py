from typing import List

from app.database.database import Database
from app.schemas.github_schemas import (
    Ordering,
    Repository,
    RepositoryActivity,
    RepositoryActivityFilter,
)


class GithubService:
    def __init__(self, repository_db: Database):
        self.repository_db = repository_db

    async def get_top100_repositories(self, ordering: Ordering) -> List[Repository]:
        query = f"SELECT * FROM repositories ORDER BY {ordering.order_by.value} DESC"
        repos_raw = await self.repository_db.execute_query(query)
        return [Repository(**repo) for repo in repos_raw]

    async def get_repository_activity(self, params: RepositoryActivityFilter) -> List[RepositoryActivity]:
        query = """
            SELECT
                commits.date,
                COUNT(commits.commit_id) AS commits,
                ARRAY_AGG(DISTINCT authors.name) AS authors
            FROM commits
            JOIN authors ON commits.author_id = authors.author_id
            WHERE commits.repo_id = $1
        """
        repo_id_record = await self.repository_db.execute_query(
            "SELECT repo_id FROM repositories WHERE owner = $1 AND repo = $2", params.owner, params.repo)
        if not repo_id_record:
            return []
        repo_id = repo_id_record[0]["repo_id"]
        query += " AND commits.repo_id = $1"
        db_params = [repo_id]

        if params.since:
            query += " AND commits.date >= $2"
            db_params.append(params.since)

        if params.until:
            query += " AND commits.date <= $3"
            db_params.append(params.until)

        query += " GROUP BY commits.date"

        repos_raw = await self.repository_db.execute_query(query, *db_params)
        return [RepositoryActivity(**repo) for repo in repos_raw]
