#!/usr/bin/env python3
"""
Generate fingerprints for test songs locally and export to SQL dump.
This script should be run locally with docker-compose to generate seed_data.sql
"""

import os
import sys
import subprocess
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.models import Artist, Song, Fingerprint
from app.services.fingerprint import fingerprint_audio
from app.services.file_handler import validate_audio_file, save_audio_file

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
TEST_SONGS_DIR = Path(__file__).parent.parent / "test_songs"
SQL_DUMP_FILE = Path(__file__).parent.parent / "seed_data.sql"


def create_test_artists(db_session):
    """Create test artists"""
    artists_data = [
        {"name": "Test Artist 1"},
        {"name": "Test Artist 2"},
        {"name": "Test Artist 3"},
    ]

    artists = []
    for artist_data in artists_data:
        existing = db_session.query(Artist).filter(Artist.name == artist_data["name"]).first()
        if existing:
            artists.append(existing)
            print(f"  ✓ Artist '{artist_data['name']}' already exists")
        else:
            artist = Artist(**artist_data)
            db_session.add(artist)
            db_session.commit()
            db_session.refresh(artist)
            artists.append(artist)
            print(f"  ✓ Created artist '{artist.name}'")

    return artists


def process_audio_file(file_path, artist_id, db_session):
    """Process a single audio file and generate fingerprints"""
    file_name = file_path.stem
    file_ext = file_path.suffix

    print(f"\n  Processing: {file_name}{file_ext}")

    # Create song entry
    song = Song(
        title=file_name.replace('_', ' ').title(),
        artist_id=artist_id,
        file_format=file_ext.replace('.', '').upper(),
        is_processed=False
    )
    db_session.add(song)
    db_session.commit()
    db_session.refresh(song)

    print(f"    Created song entry: {song.title}")

    # Save file to media directory
    media_dir = Path(__file__).parent.parent / "media"
    media_dir.mkdir(exist_ok=True)

    dest_path = media_dir / f"{song.id}{file_ext}"
    import shutil
    shutil.copy(file_path, dest_path)

    song.file_path = str(dest_path)
    db_session.commit()

    # Generate fingerprints
    print(f"    Generating fingerprints...")
    try:
        fingerprints = fingerprint_audio(str(dest_path))

        if len(fingerprints) == 0:
            print(f"    ⚠️  No fingerprints generated")
            song.is_processed = False
            db_session.commit()
            return song

        # Batch insert fingerprints
        fingerprint_objects = [
            Fingerprint(
                song_id=song.id,
                hash_value=hash_value,
                time_offset=time_offset
            )
            for hash_value, time_offset in fingerprints
        ]

        db_session.bulk_save_objects(fingerprint_objects)
        song.is_processed = True
        db_session.commit()

        print(f"    ✓ Generated {len(fingerprints)} fingerprints")
        return song

    except Exception as e:
        print(f"    ❌ Error generating fingerprints: {e}")
        song.is_processed = False
        db_session.commit()
        return song


def export_to_sql_dump():
    """Export database to SQL dump file"""
    print(f"\n{'='*60}")
    print("Exporting database to SQL dump...")
    print(f"{'='*60}")

    # Parse DATABASE_URL to get connection details
    if DATABASE_URL.startswith("postgresql://"):
        # Remove protocol
        db_url = DATABASE_URL.replace("postgresql://", "")
        # Split user:password@host:port/db
        parts = db_url.split("@")
        user_pass = parts[0]
        host_port_db = parts[1]

        user, password = user_pass.split(":")
        host, port_db = host_port_db.split(":")
        port, database = port_db.split("/")

        # Set PGPASSWORD environment variable for pg_dump
        env = os.environ.copy()
        env["PGPASSWORD"] = password

        # Run pg_dump
        cmd = [
            "pg_dump",
            f"-h{host}",
            f"-p{port}",
            f"-U{user}",
            "-d", database,
            "--data-only",
            "--disable-triggers",
            "--no-owner",
            "--no-acl",
            "-f", str(SQL_DUMP_FILE)
        ]

        try:
            subprocess.run(cmd, env=env, check=True)
            print(f"✓ SQL dump saved to {SQL_DUMP_FILE}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running pg_dump: {e}")
            print("Note: Make sure pg_dump is installed and database is accessible")
            return False
    else:
        print(f"❌ Unsupported DATABASE_URL format: {DATABASE_URL}")
        return False


def main():
    print(f"{'='*60}")
    print("Shazam Clone - Local Fingerprint Generator")
    print(f"{'='*60}")

    # Check if test_songs directory exists and has files
    if not TEST_SONGS_DIR.exists():
        print(f"❌ Test songs directory not found: {TEST_SONGS_DIR}")
        print("Please place audio files in the test_songs/ directory")
        sys.exit(1)

    audio_files = list(TEST_SONGS_DIR.glob("*.mp3")) + list(TEST_SONGS_DIR.glob("*.wav"))
    if not audio_files:
        print(f"❌ No audio files found in {TEST_SONGS_DIR}")
        print("Please add MP3 or WAV files to the test_songs/ directory")
        sys.exit(1)

    print(f"\nFound {len(audio_files)} audio file(s):")
    for f in audio_files:
        print(f"  - {f.name}")

    # Connect to database
    print(f"\nConnecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Create artists
        print(f"\n{'='*60}")
        print("Creating test artists...")
        print(f"{'='*60}")
        artists = create_test_artists(db)

        # Process audio files
        print(f"\n{'='*60}")
        print("Processing audio files...")
        print(f"{'='*60}")

        for i, audio_file in enumerate(audio_files):
            artist = artists[i % len(artists)]  # Round-robin artist assignment
            process_audio_file(audio_file, artist.id, db)

        # Export to SQL
        if export_to_sql_dump():
            print(f"\n{'='*60}")
            print("✓ Success!")
            print(f"{'='*60}")
            print(f"Processed {len(audio_files)} songs")
            print(f"SQL dump saved to: {SQL_DUMP_FILE}")
            print(f"\nNext steps:")
            print(f"1. Commit {SQL_DUMP_FILE.name} to the repository")
            print(f"2. Add test_songs/ to .gitignore (don't commit audio files)")
            print(f"3. Deploy to Render")
        else:
            print(f"\n{'='*60}")
            print("⚠️  SQL export failed")
            print(f"{'='*60}")
            print("Fingerprints were generated but SQL dump failed.")
            print("You can manually export the database or use an alternative method.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
