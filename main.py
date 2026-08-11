from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth import router as auth_router
from database import get_db, init_db
from models import User
from schemas import UserCreate, UserPatch, UserResponse, UserUpdate

# ── Rate limiter ───────────────────────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


# ── App lifecycle ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


# ── App instance ───────────────────────────────────────────────────────────────

description = """
A live, publicly accessible REST API built as a QA portfolio project.

Full CRUD for a **/users** resource — designed as a real test basis for Postman / Newman test suites.

- 10 seed users reset daily at **03:00 UTC**
- Input validation with proper HTTP status codes
- Rate limiting: 100 requests/min per IP

**Swagger UI tip:** Use *Try it out* on any endpoint to send real requests against the live API.

**Source:** https://github.com/GCarlomagno/qa-live-api
"""

app = FastAPI(
    title="Swagger QA Live API",
    description=description,
    version="2.0.0",
    lifespan=lifespan,
    servers=[{"url": "https://api.testacode.com", "description": "Live API"}],
)

app.include_router(auth_router)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Helper ─────────────────────────────────────────────────────────────────────

def _get_user_or_404(user_id: int, db: Session) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user


def _handle_integrity_error(exc: IntegrityError) -> None:
    msg = str(exc.orig).lower()
    if "username" in msg:
        raise HTTPException(status_code=409, detail="Username already exists")
    if "email" in msg:
        raise HTTPException(status_code=409, detail="Email already exists")
    raise HTTPException(status_code=409, detail="Duplicate value on a unique field")


def _user_to_response(user: User) -> UserResponse:
    return UserResponse.from_orm(user)


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
@limiter.limit("100/minute")
def root(request: Request):
    """API info and link to interactive docs."""
    return {
        "name": "QA Live API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "source": "https://github.com/GCarlomagno/qa-live-api",
    }


@app.get("/health", tags=["Info"])
@limiter.limit("100/minute")
def health(request: Request):
    """Health check endpoint."""
    return {"status": "ok"}


# ── Users ──────────────────────────────────────────────────────────────────────

@app.get("/users", response_model=list[UserResponse], tags=["Users"])
@limiter.limit("100/minute")
def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Return a paginated list of users."""
    users = db.query(User).offset(skip).limit(limit).all()
    return [_user_to_response(u) for u in users]


@app.post("/users", response_model=UserResponse, status_code=201, tags=["Users"])
@limiter.limit("100/minute")
def create_user(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user. Returns the created object with its assigned id."""
    address = payload.address
    user = User(
        name=payload.name,
        username=payload.username,
        email=payload.email,
        phone=payload.phone,
        website=payload.website,
        street=address.street if address else None,
        city=address.city if address else None,
        zipcode=address.zipcode if address else None,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        _handle_integrity_error(exc)
    return _user_to_response(user)


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
@limiter.limit("100/minute")
def get_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """Fetch a single user by id."""
    return _user_to_response(_get_user_or_404(user_id, db))


@app.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
@limiter.limit("100/minute")
def replace_user(
    request: Request,
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
):
    """Full replacement of a user's fields."""
    user = _get_user_or_404(user_id, db)
    address = payload.address
    user.name = payload.name
    user.username = payload.username
    user.email = payload.email
    user.phone = payload.phone
    user.website = payload.website
    user.street = address.street if address else None
    user.city = address.city if address else None
    user.zipcode = address.zipcode if address else None
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        _handle_integrity_error(exc)
    return _user_to_response(user)


@app.patch("/users/{user_id}", response_model=UserResponse, tags=["Users"])
@limiter.limit("100/minute")
def patch_user(
    request: Request,
    user_id: int,
    payload: UserPatch,
    db: Session = Depends(get_db),
):
    """Partial update — only the supplied fields are changed."""
    user = _get_user_or_404(user_id, db)
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=422, detail="Request body must include at least one field")
    for field, value in updates.items():
        if field == "address" and value is not None:
            addr = payload.address
            if addr.street is not None:
                user.street = addr.street
            if addr.city is not None:
                user.city = addr.city
            if addr.zipcode is not None:
                user.zipcode = addr.zipcode
        elif field != "address":
            setattr(user, field, value)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        _handle_integrity_error(exc)
    return _user_to_response(user)


@app.delete("/users/{user_id}", tags=["Users"])
@limiter.limit("100/minute")
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """Delete a user by id."""
    user = _get_user_or_404(user_id, db)
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}