from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


Severity = Literal["P1", "P2", "P3", "P4"]

IncidentStatus = Literal[
    "open",
    "investigating",
    "resolved",
    "closed"
]


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Literal["user", "admin"] = "user"


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: Severity = "P3"
    assigned_to: str | None = None


class IncidentUpdate(BaseModel):
    status: IncidentStatus | None = None
    severity: Severity | None = None
    assigned_to: str | None = None


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    assigned_to: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )