#!/usr/bin/env python3
"""
Seed the Render database with pre-generated fingerprint data.
This script imports the seed_data.sql file on first deployment.
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SQL_DUMP_FILE = Path(__file__).parent.parent / "seed_data.sql"


def is_database_empty(engine):
    """Check if the database has any songs"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM songs"))
            count = result.scalar()
            return count == 0
    except Exception as e:
        print(f"Error checking database: {e}")
        return False


def import_sql_dump(engine, sql_file):
    """Import SQL dump file into database"""
    if not sql_file.exists():
        print(f"⚠️  SQL dump file not found: {sql_file}")
        print("Database will be empty. You'll need to seed it manually.")
        return False

    print(f"Importing SQL dump from {sql_file}...")

    try:
        with open(sql_file, 'r') as f:
            sql_content = f.read()

        # Split by statements and execute
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]

        with engine.connect() as conn:
            for i, statement in enumerate(statements):
                if statement and not statement.startswith('--'):
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        print(f"  Warning: Failed to execute statement {i+1}: {e}")
                        # Continue with other statements

        print(f"✓ Imported {len(statements)} SQL statements")
        return True

    except Exception as e:
        print(f"❌ Error importing SQL dump: {e}")
        return False


def main():
    print(f"{'='*60}")
    print("Shazam Clone - Database Seeder (Render)")
    print(f"{'='*60}")

    if not DATABASE_URL:
        print("❌ DATABASE_URL not set")
        sys.exit(1)

    print(f"Connecting to database...")

    try:
        engine = create_engine(DATABASE_URL)

        # Check if database is empty
        if is_database_empty(engine):
            print("Database is empty. Attempting to seed...")
            if import_sql_dump(engine, SQL_DUMP_FILE):
                print("✓ Database seeded successfully")
            else:
                print("⚠️  Database seeding failed or skipped")
        else:
            print("Database already contains data. Skipping seed.")
            print("✓ Database is ready")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
