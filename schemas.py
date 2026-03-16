from pydantic import BaseModel, EmailStr, field_validator


# ── Shared validators ──────────────────────────────────────────────────────────

def _non_empty(v: str | None, field_name: str) -> str:
    if v is not None and v.strip() == "":
        raise ValueError(f"{field_name} must not be empty or whitespace")
    return v


# ── Request schemas ────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Used on POST /users — all fields required."""
    name: str
    username: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        return _non_empty(v, "name")

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        return _non_empty(v, "username")


class UserUpdate(BaseModel):
    """Used on PUT /users/{id} — all fields required (full replace)."""
    name: str
    username: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        return _non_empty(v, "name")

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        return _non_empty(v, "username")


class UserPatch(BaseModel):
    """Used on PATCH /users/{id} — all fields optional."""
    name: str | None = None
    username: str | None = None
    email: EmailStr | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        return _non_empty(v, "name")

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str | None) -> str | None:
        return _non_empty(v, "username")


# ── Response schema ────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    """Returned by all endpoints that include user data."""
    id: int
    name: str
    username: str
    email: str

    model_config = {"from_attributes": True}  # allows ORM → Pydantic conversion