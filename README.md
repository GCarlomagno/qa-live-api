# QA Live API

A **live, publicly accessible REST API** built as a QA portfolio project — designed as a real test basis for Postman / Newman test suites.

If you are a QA student looking for a real API to practice against, you are in the right place. No sign-up, no API keys, no setup required.

**Live URL:** http://api.testacode.com  
**Swagger UI:** http://api.testacode.com/docs  
**ReDoc:** http://api.testacode.com/redoc  
**GitHub:** https://github.com/GCarlomagno/qa-live-api

---

## What is this?

This API simulates a simple user management system with full CRUD operations. It behaves like a real production API — it validates input, returns proper HTTP status codes, and persists data between requests.

The test object is intentionally simple so testers can focus on **test design and execution**, not on understanding a complex domain.

The seed data contains **intentional defects**. Part of the exercise is designing test cases that detect them. The defect list is published at the bottom of this document — but try to find them yourself first.

> ⚠️ **Important precondition:** This is a **shared test environment**. If you or another tester deletes a user, it stays deleted until the daily reset at 03:00 UTC. Design your test cases with this shared state in mind.

---

## Test Basis

### User schema

The system under test (SUT) manages users with the following structure:

```json
{
  "id": 1,
  "name": "Alice Smith",
  "username": "alicesmith",
  "email": "alice.smith@example.com",
  "phone": "+351 912 345 678",
  "website": "http://alice.example.com",
  "address": {
    "street": "10 Rua Augusta",
    "city": "Lisbon",
    "zipcode": "1100-048"
  }
}
```

### Seed data — known test fixtures

Every day at **03:00 UTC** the database resets to these 10 known test fixtures. Some contain intentional defects — can you find them?

| id | name | username | email |
|---|---|---|---|
| 1 | Alice Smith | alicesmith | alice.smith@example.com |
| 2 | Bob Johnson | bobjohnson | bob.johnson@example.com |
| 3 | Carol White | carolwhite | carol.white@example.com |
| 4 | David Brown | davidbrown | david.brown@example.com |
| 5 | Eva Martinez | evamartinez | eva.martinez@example.com |
| 6 | Frank Lee | franklee | frank.lee@example.com |
| 7 | Grace Kim | gracekim | grace.kim@example.com |
| 8 | Henry Costa | henrycosta | henry.costa@example.com |
| 9 | Isla Nguyen | islanguyen | isla.nguyen@example.com |
| 10 | James Okafor | jamesokafor | james.okafor@example.com |

Use ids 11+ for test users created during test execution to avoid conflicts with the seed fixtures.

---

## Test Conditions

### Endpoints

| Method | Path | Description | Expected HTTP response code |
|---|---|---|---|
| GET | `/` | API info + links | 200 |
| GET | `/health` | Health check | 200 |
| GET | `/users` | List all users (`?skip=&limit=`) | 200 |
| POST | `/users` | Create a user | 201 |
| GET | `/users/{id}` | Get user by id | 200 |
| PUT | `/users/{id}` | Full replace by id | 200 |
| PATCH | `/users/{id}` | Partial update by id | 200 |
| DELETE | `/users/{id}` | Delete by id | 200 |

### Input validation rules

These rules define the **valid equivalence partitions** for each field:

| Field | Required on POST/PUT | Required on PATCH | Constraints |
|---|---|---|---|
| `name` | Yes | No | Non-empty string |
| `username` | Yes | No | Non-empty string, unique across all users |
| `email` | Yes | No | Valid email format, unique across all users |
| `phone` | No | No | String, no format validation |
| `website` | No | No | String, no format validation |
| `address.street` | No | No | String |
| `address.city` | No | No | String |
| `address.zipcode` | No | No | String |

### HTTP response code catalogue

| Condition | Expected result |
|---|---|
| Valid request — GET or DELETE | 200 OK |
| Valid request — POST | 201 Created |
| Valid request — PUT or PATCH | 200 OK |
| Invalid input — missing or malformed field | 422 Unprocessable Entity |
| Non-existent resource | 404 Not Found |
| Duplicate unique field (username or email) | 409 Conflict |
| Rate limit exceeded (> 100 requests/min per IP) | 429 Too Many Requests |

---

## Test Design

### Equivalence partitioning

Based on the input validation rules, the following equivalence classes apply to POST /users:

**Valid partition (expected result: 201 Created)**
- All required fields present, non-empty, valid email, unique username and email

**Invalid partitions (expected result: 422 Unprocessable Entity)**
- Missing `name`
- Missing `username`
- Missing `email`
- Empty string for `name` or `username`
- Malformed email format (e.g. `notanemail`, `user@`, `user@domain`)

**Invalid partition (expected result: 409 Conflict)**
- `username` already exists in the database
- `email` already exists in the database

### Boundary value analysis

For pagination parameters on GET /users:

| Parameter | Boundary | Expected behaviour |
|---|---|---|
| `skip=0` | Lower boundary | Returns users from the beginning |
| `limit=1` | Lower boundary | Returns exactly 1 user |
| `limit=20` | Default value | Returns up to 20 users |
| `skip` > total users | Upper boundary | Returns empty list |

### Schema validation

For each user returned by GET /users and GET /users/{id}, verify:

- `id` is a positive integer
- `name` is a non-empty string
- `username` is a non-empty string
- `email` matches a valid email format
- `phone` is a string or null
- `website` starts with `http://` or `https://` if present
- `address.city` is a non-numeric string if present
- `address.zipcode` is a non-empty string if present

---

## Suggested Test Cases

### Positive testing

| TC ID | Test condition | Precondition | Steps | Expected result |
|---|---|---|---|---|
| TC-01 | GET all users | Seed data present | GET /users | 200, body contains 10 users |
| TC-02 | GET user by valid id | Seed data present | GET /users/1 | 200, body matches Alice Smith |
| TC-03 | Create a new user | Username and email are unique | POST /users with valid body | 201, body contains user with assigned id |
| TC-04 | Full replace of a user | User with id exists | PUT /users/{id} with all fields | 200, all fields updated |
| TC-05 | Partial update of a user | User with id exists | PATCH /users/{id} with one field | 200, only patched field changed |
| TC-06 | Delete a user | User with id exists | DELETE /users/{id} | 200, confirmation message |
| TC-07 | Paginate results | At least 3 users exist | GET /users?skip=2&limit=2 | 200, returns correct subset |
| TC-08 | Create user with nested address | — | POST /users with address object | 201, address fields present in response |

### Negative testing

| TC ID | Test condition | Precondition | Steps | Expected result |
|---|---|---|---|---|
| TC-09 | GET non-existent user | User id does not exist | GET /users/9999 | 404 Not Found |
| TC-10 | POST with missing name | — | POST /users without `name` | 422 Unprocessable Entity |
| TC-11 | POST with missing email | — | POST /users without `email` | 422 Unprocessable Entity |
| TC-12 | POST with invalid email | — | POST /users with `email: "notanemail"` | 422 Unprocessable Entity |
| TC-13 | POST with empty name | — | POST /users with `name: ""` | 422 Unprocessable Entity |
| TC-14 | POST with duplicate username | Username already exists | POST /users with existing username | 409 Conflict |
| TC-15 | POST with duplicate email | Email already exists | POST /users with existing email | 409 Conflict |
| TC-16 | PATCH with empty body | User with id exists | PATCH /users/{id} with `{}` | 422 Unprocessable Entity |
| TC-17 | PUT with missing required field | User with id exists | PUT /users/{id} without `name` | 422 Unprocessable Entity |
| TC-18 | Rate limit exceeded | — | > 100 requests/min to any endpoint | 429 Too Many Requests |

### Schema validation test cases

| TC ID | Test condition | Steps | Expected result |
|---|---|---|---|
| TC-19 | All emails are valid format | GET /users, inspect all records | All `email` fields match valid email format |
| TC-20 | All phone fields are present | GET /users, inspect all records | No `phone` field is null |
| TC-21 | All websites have valid protocol | GET /users, inspect all records | All `website` fields start with `http://` or `https://` |
| TC-22 | All city fields are non-numeric | GET /users, inspect all records | No `city` field contains only digits |
| TC-23 | All zipcodes are non-empty | GET /users, inspect all records | No `zipcode` field is an empty string |

### Test chaining (end-to-end flows)

| TC ID | Flow | Expected result |
|---|---|---|
| TC-24 | POST → GET | Create user, GET by returned id, assert response matches created data |
| TC-25 | POST → DELETE → GET | Create user, DELETE it, GET it, assert 404 |
| TC-26 | POST → PATCH → GET | Create user, PATCH one field, GET it, assert only that field changed |

---

## curl examples

```bash
# Health check
curl http://api.testacode.com/health

# List all users
curl http://api.testacode.com/users

# Paginate — skip first 2, return next 2
curl "http://api.testacode.com/users?skip=2&limit=2"

# Get one user
curl http://api.testacode.com/users/1

# Create a user with nested address
curl -X POST http://api.testacode.com/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "username": "janedoe",
    "email": "jane.doe@example.com",
    "phone": "+351 999 888 777",
    "website": "http://janedoe.com",
    "address": {
      "street": "5 Test Street",
      "city": "Porto",
      "zipcode": "4000-001"
    }
  }'

# Full replace
curl -X PUT http://api.testacode.com/users/11 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "username": "janedoe",
    "email": "jane.doe@example.com"
  }'

# Partial update
curl -X PATCH http://api.testacode.com/users/11 \
  -H "Content-Type: application/json" \
  -d '{"phone": "+351 111 222 333"}'

# Delete
curl -X DELETE http://api.testacode.com/users/11

# Trigger 404
curl http://api.testacode.com/users/9999

# Trigger 422 — missing email
curl -X POST http://api.testacode.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"No Email","username":"noemail"}'

# Trigger 409 — duplicate username
curl -X POST http://api.testacode.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice Copy","username":"alicesmith","email":"copy@example.com"}'
```

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

Open http://localhost:8000/docs to access the local Swagger UI.

---

## Defect register

<details>
<summary>⚠️ Click to reveal — try to find these yourself first</summary>

| Defect ID | User | Field | Issue |
|---|---|---|---|
| D-01 | User 3 — Carol White | `email` | Missing TLD: `carol.white@example` |
| D-02 | User 5 — Eva Martinez | `phone` | Field is `null` — should not be missing |
| D-03 | User 6 — Frank Lee | `city` | Value is `"12345"` — numeric string instead of city name |
| D-04 | User 7 — Grace Kim | `zipcode` | Empty string instead of valid zipcode |
| D-05 | User 9 — Isla Nguyen | `website` | Malformed protocol: `htp://` instead of `http://` |

</details>

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