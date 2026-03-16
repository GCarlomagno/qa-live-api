"""
seed.py — wipes the users table and inserts 10 seed users.

Intentional data defects for QA students to find:
  D-01  User 3  (Carol White)   email missing TLD: "carol.white@example"
  D-02  User 5  (Eva Martinez)  phone is None — field missing
  D-03  User 6  (Frank Lee)     city is "12345" — numeric value instead of city name
  D-04  User 7  (Grace Kim)     zipcode is empty string instead of valid zipcode
  D-05  User 9  (Isla Nguyen)   website has malformed protocol: "htp://islanguyen.au"

Run manually:  python seed.py
Run via cron:  0 3 * * * /var/www/qa-live-api/venv/bin/python /var/www/qa-live-api/seed.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, init_db
from models import User

SEED_USERS = [
    User(
        id=1,
        name="Alice Smith",
        username="alicesmith",
        email="alice.smith@example.com",
        phone="+351 912 345 678",
        website="http://alice.example.com",
        street="10 Rua Augusta",
        city="Lisbon",
        zipcode="1100-048",
    ),
    User(
        id=2,
        name="Bob Johnson",
        username="bobjohnson",
        email="bob.johnson@example.com",
        phone="+44 7700 900123",
        website="http://bobjohnson.dev",
        street="221B Baker Street",
        city="London",
        zipcode="NW1 6XE",
    ),
    User(
        id=3,
        name="Carol White",
        username="carolwhite",
        # ⚠️ D-01: malformed email — missing TLD
        email="carol.white@example",
        phone="+1 415 555 0198",
        website="http://carolwhite.io",
        street="742 Evergreen Terrace",
        city="Springfield",
        zipcode="62701",
    ),
    User(
        id=4,
        name="David Brown",
        username="davidbrown",
        email="david.brown@example.com",
        phone="+49 30 12345678",
        website="http://davidbrown.de",
        street="Unter den Linden 1",
        city="Berlin",
        zipcode="10117",
    ),
    User(
        id=5,
        name="Eva Martinez",
        username="evamartinez",
        email="eva.martinez@example.com",
        # ⚠️ D-02: phone is None — field missing
        phone=None,
        website="http://evamartinez.es",
        street="Calle Gran Via 28",
        city="Madrid",
        zipcode="28013",
    ),
    User(
        id=6,
        name="Frank Lee",
        username="franklee",
        email="frank.lee@example.com",
        phone="+1 212 555 0142",
        website="http://franklee.com",
        street="350 Fifth Avenue",
        # ⚠️ D-03: city is a numeric string instead of a city name
        city="12345",
        zipcode="10118",
    ),
    User(
        id=7,
        name="Grace Kim",
        username="gracekim",
        email="grace.kim@example.com",
        phone="+82 10 1234 5678",
        website="http://gracekim.kr",
        street="Gangnam-daero 396",
        city="Seoul",
        # ⚠️ D-04: zipcode is empty string
        zipcode="",
    ),
    User(
        id=8,
        name="Henry Costa",
        username="henrycosta",
        email="henry.costa@example.com",
        phone="+55 11 91234 5678",
        website="http://henrycosta.br",
        street="Avenida Paulista 1000",
        city="Sao Paulo",
        zipcode="01310-100",
    ),
    User(
        id=9,
        name="Isla Nguyen",
        username="islanguyen",
        email="isla.nguyen@example.com",
        phone="+61 412 345 678",
        # ⚠️ D-05: malformed URL protocol — htp:// instead of http://
        website="htp://islanguyen.au",
        street="1 Harbour Bridge Rd",
        city="Sydney",
        zipcode="2000",
    ),
    User(
        id=10,
        name="James Okafor",
        username="jamesokafor",
        email="james.okafor@example.com",
        phone="+234 801 234 5678",
        website="http://jamesokafor.ng",
        street="15 Broad Street",
        city="Lagos",
        zipcode="101001",
    ),
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
        for user in SEED_USERS:
            db.add(user)
        db.commit()
        print(f"✅  Seeded {len(SEED_USERS)} users successfully.")
    except Exception as exc:
        db.rollback()
        print(f"❌  Seed failed: {exc}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()