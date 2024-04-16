from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from ..database import Database, get_db
from ..schemas import Repository, RepositoryActivity

router = APIRouter(prefix="/api/repos", tags=["Github"])


@router.get("/top100", response_model=List[Repository])
async def top100(order_by: Optional[str] = None, db: Database = Depends(get_db)):
    if order_by:
        repos = await db.execute_query("SELECT * FROM repositories ORDER BY %s", order_by)
    else:
        repos = await db.execute_query("SELECT * FROM repositories")
    return [dict(repo) for repo in repos]


@router.get("/{owner}/{repo}/activity", response_model=List[RepositoryActivity])
async def activity(owner: str, repo: str, since: Optional[datetime] = None, until: Optional[datetime] = None, db: Database = Depends(get_db)):
    repo_id_record = await db.execute_query(
        "SELECT repo_id FROM repositories WHERE owner = $1 AND repo = $2", owner, repo)
    if not repo_id_record:
        raise HTTPException(status_code=404, detail="Repository not found")

    query = """
        SELECT
            commits.date,
            COUNT(commits.commit_id) AS commits,
            ARRAY_AGG(DISTINCT authors.name) AS authors
        FROM commits
        JOIN authors ON commits.author_id = authors.author_id
        WHERE commits.repo_id = $1
    """
    repo_id = repo_id_record[0]["repo_id"]
    params = [repo_id]

    if since:
        query += " AND commits.date >= $2"
        params.append(since)

    if until:
        query += " AND commits.date <= $3"
        params.append(until)

    query += " GROUP BY commits.date"

    repos = await db.execute_query(query, *params)
    return [dict(repo) for repo in repos]
