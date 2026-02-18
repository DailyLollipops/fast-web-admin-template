# Generated code for RoleAccessControl model

from typing import Annotated

from fastapi import APIRouter
from pydantic import BaseModel

from api.database.models.user import User
from api.routes.auth import get_authenticated_user
from api.routes.auth.core import all_permissions


router = APIRouter(tags=['Permission'])

class PermissionListResponse(BaseModel):
    total: int
    data: list[dict]


@router.get('/permissions', response_model=PermissionListResponse)
async def get_all_permissions(
    current_user: Annotated[User, get_authenticated_user('permissions.read')],
):
    data = [
        {
            "id": idx,
            "name": perm
        }
        for idx, perm in enumerate(all_permissions)
    ]

    return PermissionListResponse(total=len(all_permissions), data=data)
