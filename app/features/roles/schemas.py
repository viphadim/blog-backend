from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PermissionResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class RoleWithPermissionsResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    permissions: list[PermissionResponse] = []

    model_config = {"from_attributes": True}
    @classmethod
    def from_role(cls, role) -> "RoleWithPermissionsResponse":
        return cls(
            id=role.id,
            name=role.name,
            description=role.description,
            created_at=role.created_at,
            #  extract permissions from role_permissions manually
            permissions=[
                PermissionResponse.model_validate(rp.permission)
                for rp in role.role_permissions
                if rp.permission
            ],
        )