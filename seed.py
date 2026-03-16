"""
seed.py — wipes the users table and inserts 5 clean seed users.
Run manually:  python seed.py
Run via cron:  0 3 * * * /var/www/qa-live-api/venv/bin/python /var/www/qa-live-api/seed.py
"""

import sys
import os

# Allow running from any working directory
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, init_db
from models import User

SEED_USERS = [
    User(id=1, name="Alice Smith",   username="alicesmith",   email="alice.smith@example.com"),
    User(id=2, name="Bob Johnson",   username="bobjohnson",   email="bob.johnson@example.com"),
    User(id=3, name="Carol White",   username="carolwhite",   email="carol.white@example.com"),
    User(id=4, name="David Brown",   username="davidbrown",   email="david.brown@example.com"),
    User(id=5, name="Eva Martinez",  username="evamartinez",  email="eva.martinez@example.com"),
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        # Wipe existing rows and reset the auto-increment counter
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