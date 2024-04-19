import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class OrderEnum(str, Enum):
    stars = "stars"
    watchers = "watchers"
    forks = "forks"
    open_issues = "open_issues"


class Ordering(BaseModel):
    order_by: OrderEnum = OrderEnum.stars


class RepositoryActivityFilter(BaseModel):
    owner: str
    repo: str
    since: Optional[datetime.date] = None
    until: Optional[datetime.date] = None


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
