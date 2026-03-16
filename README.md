# QA Live API

A live, publicly accessible REST API built as a QA portfolio project.  
Full CRUD for a `/users` resource — designed as a real backend target for Postman / Newman test suites.

**Live URL:** http://api.testacode.com  
**Swagger UI:** http://api.testacode.com/docs  
**ReDoc:** http://api.testacode.com/redoc

---

## Tech stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Framework | FastAPI |
| Database | SQLite via SQLAlchemy |
| Server | Uvicorn |
| Process manager | PM2 |
| Reverse proxy | Nginx |
| Rate limiting | slowapi (100 req/min per IP) |
| Seed reset | Daily cron at 03:00 UTC |

---

## User schema

```json
{
  "id": 1,
  "name": "Alice Smith",
  "username": "alicesmith",
  "email": "alice.smith@example.com"
}
```

---

## Endpoints

| Method | Path | Description | Success code |
|---|---|---|---|
| GET | `/` | API info + links | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/users` | List all users (`?skip=&limit=`) | 200 |
| POST | `/users` | Create a user | 201 |
| GET | `/users/{id}` | Get user by id | 200 |
| PUT | `/users/{id}` | Full replace by id | 200 |
| PATCH | `/users/{id}` | Partial update by id | 200 |
| DELETE | `/users/{id}` | Delete by id | 200 |

### HTTP status codes

| Scenario | Code |
|---|---|
| Successful GET / DELETE | 200 |
| Successful POST | 201 |
| Successful PUT / PATCH | 200 |
| Validation error | 422 |
| User not found | 404 |
| Duplicate username or email | 409 |

---

## curl examples

```bash
# Health check
curl http://api.testacode.com/health

# List users (default limit 20)
curl http://api.testacode.com/users

# Paginate
curl "http://api.testacode.com/users?skip=0&limit=3"

# Get one user
curl http://api.testacode.com/users/1

# Create a user
curl -X POST http://api.testacode.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","username":"janedoe","email":"jane.doe@example.com"}'

# Full replace
curl -X PUT http://api.testacode.com/users/6 \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","username":"janedoe","email":"jane.doe@example.com"}'

# Partial update (email only)
curl -X PATCH http://api.testacode.com/users/6 \
  -H "Content-Type: application/json" \
  -d '{"email":"new.email@example.com"}'

# Delete
curl -X DELETE http://api.testacode.com/users/6

# Trigger a 404
curl http://api.testacode.com/users/9999

# Trigger a 422 (missing required field)
curl -X POST http://api.testacode.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"No Email"}'

# Trigger a 409 (duplicate username)
curl -X POST http://api.testacode.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice Smith","username":"alicesmith","email":"other@example.com"}'
```

---

## Validation rules

- `name` — required on POST/PUT, non-empty string  
- `username` — required on POST/PUT, non-empty string, **unique**  
- `email` — required on POST/PUT, valid email format, **unique**  
- All fields optional on PATCH (at least one must be supplied)

---

## Running locally

```bash
git clone https://github.com/GCarlomagno/qa-live-api.git
cd qa-live-api
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
mkdir -p data
python seed.py
uvicorn main:app --reload
```

Open http://localhost:8000/docs

---

## Seed reset

A cron job runs `seed.py` daily at 03:00 UTC, wiping the table and restoring the 5 original users (ids 1–5). Any users you create during testing will be cleared at that time.