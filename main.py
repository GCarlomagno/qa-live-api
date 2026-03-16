from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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

app = FastAPI(
    title="QA Live API",
    description=(
        "A live, publicly accessible REST API built as a QA portfolio project. "
        "Full CRUD for a /users resource with input validation, SQLite persistence, "
        "and rate limiting. Source: https://github.com/GCarlomagno/qa-live-api"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Helper ─────────────────────────────────────────────────────────────────────

def _get_user_or_404(user_id: int, db: Session) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    return user


def _handle_integrity_error(exc: IntegrityError) -> None:
    """Translate SQLAlchemy unique-constraint violations into 409 responses."""
    msg = str(exc.orig).lower()
    if "username" in msg:
        raise HTTPException(status_code=409, detail="Username already exists")
    if "email" in msg:
        raise HTTPException(status_code=409, detail="Email already exists")
    raise HTTPException(status_code=409, detail="Duplicate value on a unique field")


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
@limiter.limit("100/minute")
def root(request: Request):
    """API info and link to interactive docs."""
    return {
        "name": "QA Live API",
        "version": "1.0.0",
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
    return db.query(User).offset(skip).limit(limit).all()


@app.post("/users", response_model=UserResponse, status_code=201, tags=["Users"])
@limiter.limit("100/minute")
def create_user(request: Request, payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user. Returns the created object with its assigned id."""
    user = User(**payload.model_dump())
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        _handle_integrity_error(exc)
    return user


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
@limiter.limit("100/minute")
def get_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """Fetch a single user by id."""
    return _get_user_or_404(user_id, db)


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
    for field, value in payload.model_dump().items():
        setattr(user, field, value)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        _handle_integrity_error(exc)
    return user


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
        setattr(user, field, value)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        _handle_integrity_error(exc)
    return user


@app.delete("/users/{user_id}", tags=["Users"])
@limiter.limit("100/minute")
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """Delete a user by id."""
    user = _get_user_or_404(user_id, db)
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}