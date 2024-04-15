import datetime
from typing import Optional

from pydantic import BaseModel


class Repository(BaseModel):
    repo: str
    owner: str
    position_cur: int
    position_prev: int
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: Optional[str] = None


class RepositoryActivity(BaseModel):
    date: datetime.date
    commits: int
    authors: list[str]
