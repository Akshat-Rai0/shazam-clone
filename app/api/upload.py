from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session, sessionmaker
from app.core.database import get_db, engine
from app.models.models import Song, Artist, Fingerprint
from app.services.file_handler import validate_audio_file, save_audio_file
from app.services.fingerprint import fingerprint_audio
import traceback

router = APIRouter(prefix="/upload", tags=["upload"])

# Create a separate session factory for background tasks
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def process_fingerprints_background(song_id: int, file_path: str):
    """Background task to generate fingerprints - runs AFTER request returns"""
    # Create new database session for background task
    db = SessionLocal()
    
    try:
        print(f"\n{'='*60}")
        print(f"🔐 Background: Processing song {song_id}")
        print(f"{'='*60}")
        
        # Generate fingerprints
        fingerprints = fingerprint_audio(file_path)
        
        if len(fingerprints) == 0:
            print(f"⚠️  No fingerprints generated for song {song_id}")
            song = db.query(Song).filter(Song.id == song_id).first()
            if song:
                song.is_processed = False
            db.commit()
            return
        
        # Batch insert
        print(f"💾 Storing {len(fingerprints)} fingerprints...")
        fingerprint_objects = [
            {
                'song_id': song_id,
                'hash_value': hash_value,
                'time_offset': time_offset
            }
            for hash_value, time_offset in fingerprints
        ]
        
        db.bulk_insert_mappings(Fingerprint, fingerprint_objects)
        
        # Mark as processed
        song = db.query(Song).filter(Song.id == song_id).first()
        if song:
            song.is_processed = True
        
        db.commit()
        print(f"✅ Song {song_id}: Stored {len(fingerprint_objects)} fingerprints")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Background processing failed for song {song_id}: {str(e)}")
        traceback.print_exc()
        db.rollback()
        
        # Mark as failed
        try:
            song = db.query(Song).filter(Song.id == song_id).first()
            if song:
                song.is_processed = False
            db.commit()
        except:
            pass
    finally:
        db.close()


@router.post("/", status_code=202)  # 202 = Accepted (processing in background)
async def upload_song(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Audio file (MP3, WAV, FLAC)"),
    title: str = Form(..., description="Song title"),
    artist_id: int = Form(..., description="Artist ID"),
    db: Session = Depends(get_db)
):
    """
    Upload song - fingerprinting happens in background
    
    Returns immediately with 202 status. Check /upload/info/{song_id} for processing status.
    """
    
    print(f"\n📤 Upload: {title}")
    
    # Verify artist
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail=f"Artist with ID {artist_id} not found")
    
    # Validate
    file_info = await validate_audio_file(file)
    
    # Create record
    db_song = Song(
        title=title,
        artist_id=artist_id,
        file_format=file_info["extension"].replace('.', '').upper(),
        is_processed=False
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    
    try:
        # Save file
        file_path, metadata = await save_audio_file(file, db_song.id)
        
        db_song.file_path = file_path
        db_song.duration = metadata.get("duration")
        db.commit()
        db.refresh(db_song)
        
        print(f"✅ File saved: {db_song.id}")
        
        # Schedule background processing
        background_tasks.add_task(
            process_fingerprints_background,
            db_song.id,
            file_path
        )
        
        print(f"⏳ Fingerprinting scheduled for background")
        
        return {
            "id": db_song.id,
            "title": db_song.title,
            "artist": {"id": artist.id, "name": artist.name},
            "duration": db_song.duration,
            "file_format": db_song.file_format,
            "is_processed": False,
            "status": "processing",
            "message": "Upload successful. Fingerprinting in progress. Check /upload/info/{id} for status."
        }
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        db.delete(db_song)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")


@router.get("/info/{song_id}")
async def get_upload_info(song_id: int, db: Session = Depends(get_db)):
    """Get processing status"""
    song = db.query(Song).filter(Song.id == song_id).first()
    
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    fingerprint_count = db.query(Fingerprint).filter(Fingerprint.song_id == song_id).count()
    
    if song.is_processed:
        status = "✅ Ready for recognition"
    elif fingerprint_count > 0:
        status = "⏳ Processing..."
    else:
        status = "⏳ Queued for processing"
    
    return {
        "song_id": song.id,
        "title": song.title,
        "artist": song.artist.name,
        "is_processed": song.is_processed,
        "fingerprint_count": fingerprint_count,
        "status": status
    }


@router.get("/status")
async def get_processing_status(db: Session = Depends(get_db)):
    """Get overview of all processing status"""
    total = db.query(Song).count()
    processed = db.query(Song).filter(Song.is_processed == True).count()
    pending = total - processed
    
    return {
        "total_songs": total,
        "processed": processed,
        "pending": pending,
        "progress_percent": round((processed / total * 100) if total > 0 else 0, 1)
    }


@router.delete("/{song_id}")
async def delete_upload(song_id: int, db: Session = Depends(get_db)):
    """Delete song"""
    song = db.query(Song).filter(Song.id == song_id).first()
    
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if song.file_path:
        from app.services.file_handler import delete_audio_file
        delete_audio_file(song.file_path)
    
    db.delete(song)
    db.commit()
    
    return {"message": f"Song '{song.title}' deleted"}
