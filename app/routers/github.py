from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from ..database import Database, get_db
from ..schemas import Repository, RepositoryActivity

router = APIRouter(prefix="/api/repos", tags=["Github"])


@router.get("/top100", response_model=List[Repository])
async def top100(order_by: Optional[str] = None, db: Database = Depends(get_db)):
    if order_by:
        db.get_cur().execute("SELECT * FROM repositories ORDER BY %s", (order_by,))
    else:
        db.get_cur().execute("SELECT * FROM repositories")
    repos = db.get_cur().fetchall()
    return [dict(repo) for repo in repos]


@router.get("/{owner}/{repo}/activity", response_model=List[RepositoryActivity])
async def activity(owner: str, repo: str, db: Database = Depends(get_db)):
    db.get_cur().execute(
        "SELECT repo_id FROM repositories WHERE owner = %s AND repo = %s", (owner, repo))
    repo_id = db.get_cur().fetchone()
    if not repo_id:
        raise HTTPException(status_code=404, detail="Repository not found")

    query = """
        SELECT
            commits.date,
            COUNT(commits.commit_id) AS commits,
            ARRAY_AGG(DISTINCT authors.name) AS authors
        FROM commits
        JOIN authors ON commits.author_id = authors.author_id
        WHERE commits.repo_id = %s
        GROUP BY commits.date
    """
    db.get_cur().execute(query, repo_id)
    repos = db.get_cur().fetchall()
    return [dict(repo) for repo in repos]
