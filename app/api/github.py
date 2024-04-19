from typing import List

from fastapi import APIRouter, Depends

from app.api.dependencies import github_service
from app.schemas.github_schemas import (
    Ordering,
    Repository,
    RepositoryActivity,
    RepositoryActivityFilter,
)
from app.services.github_service import GithubService

router = APIRouter(prefix="/api/repos", tags=["Github"])


@router.get("/top100", response_model=List[Repository])
async def top100(ordering: Ordering = Depends(), github_service: GithubService = Depends(github_service)):
    return await github_service.get_top100_repositories(ordering)


@router.get("/{owner}/{repo}/activity", response_model=List[RepositoryActivity])
async def activity(params: RepositoryActivityFilter = Depends(), github_service: GithubService = Depends(github_service)):
    return await github_service.get_repository_activity(params)
