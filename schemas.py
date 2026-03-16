from pydantic import BaseModel, EmailStr, field_validator


# ── Address ────────────────────────────────────────────────────────────────────

class Address(BaseModel):
    street: str | None = None
    city: str | None = None
    zipcode: str | None = None


# ── Shared validators ──────────────────────────────────────────────────────────

def _non_empty(v: str | None, field_name: str) -> str:
    if v is not None and v.strip() == "":
        raise ValueError(f"{field_name} must not be empty or whitespace")
    return v


# ── Request schemas ────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Used on POST /users — name, username, email required."""
    name: str
    username: str
    email: EmailStr
    phone: str | None = None
    website: str | None = None
    address: Address | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        return _non_empty(v, "name")

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        return _non_empty(v, "username")


class UserUpdate(BaseModel):
    """Used on PUT /users/{id} — all core fields required (full replace)."""
    name: str
    username: str
    email: EmailStr
    phone: str | None = None
    website: str | None = None
    address: Address | None = None

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
    phone: str | None = None
    website: str | None = None
    address: Address | None = None

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
    phone: str | None = None
    website: str | None = None
    address: Address | None = None

    @classmethod
    def from_orm(cls, user):
        return cls(
            id=user.id,
            name=user.name,
            username=user.username,
            email=user.email,
            phone=user.phone,
            website=user.website,
            address=Address(
                street=user.street,
                city=user.city,
                zipcode=user.zipcode,
            ) if any([user.street, user.city, user.zipcode]) else None,
        )

    model_config = {"from_attributes": True}