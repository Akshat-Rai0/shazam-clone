from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Song, Artist, Fingerprint
from app.services.file_handler import validate_audio_file, save_audio_file
from app.services.fingerprint import fingerprint_audio
from app.schemas.schemas import SongResponse

router = APIRouter(prefix="/upload", tags=["upload"])


def process_fingerprints(song_id: int, file_path: str, db: Session):
    """Background task to generate and store fingerprints"""
    try:
        print(f"�� Processing fingerprints for song {song_id}...")
        
        # Generate fingerprints
        fingerprints = fingerprint_audio(file_path)
        
        # Store in database
        for hash_value, time_offset in fingerprints:
            db_fingerprint = Fingerprint(
                song_id=song_id,
                hash_value=hash_value,
                time_offset=time_offset
            )
            db.add(db_fingerprint)
        
        # Mark song as processed
        song = db.query(Song).filter(Song.id == song_id).first()
        if song:
            song.is_processed = True
        
        db.commit()
        print(f"✅ Stored {len(fingerprints)} fingerprints for song {song_id}")
        
    except Exception as e:
        print(f"❌ Error processing fingerprints: {str(e)}")
        db.rollback()


@router.post("/", response_model=SongResponse, status_code=201)
async def upload_song(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Audio file (MP3, WAV, FLAC)"),
    title: str = Form(..., description="Song title"),
    artist_id: int = Form(..., description="Artist ID"),
    db: Session = Depends(get_db)
):
    """
    Upload a new song file and generate fingerprints
    
    - **file**: Audio file (MP3, WAV, or FLAC format)
    - **title**: Song title
    - **artist_id**: ID of the artist
    
    Fingerprinting happens in the background after upload completes.
    """
    
    # Verify artist exists
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail=f"Artist with ID {artist_id} not found")
    
    # Validate file
    file_info = await validate_audio_file(file)
    
    # Create song record in database
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
        # Save file and extract metadata
        file_path, metadata = await save_audio_file(file, db_song.id)
        
        # Update song with file path and metadata
        db_song.file_path = file_path
        db_song.duration = metadata.get("duration")
        db.commit()
        db.refresh(db_song)
        
        # Schedule fingerprinting as background task
        background_tasks.add_task(process_fingerprints, db_song.id, file_path, db)
        
        return db_song
        
    except Exception as e:
        # Rollback if file save fails
        db.delete(db_song)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


@router.get("/info/{song_id}")
async def get_upload_info(song_id: int, db: Session = Depends(get_db)):
    """Get upload and processing information for a song"""
    song = db.query(Song).filter(Song.id == song_id).first()
    
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if not song.file_path:
        raise HTTPException(status_code=404, detail="No file uploaded for this song")
    
    from app.services.file_handler import get_file_info
    
    file_info = get_file_info(song.file_path)
    
    # Count fingerprints
    fingerprint_count = db.query(Fingerprint).filter(Fingerprint.song_id == song_id).count()
    
    return {
        "song_id": song.id,
        "title": song.title,
        "artist": song.artist.name,
        "file_info": file_info,
        "is_processed": song.is_processed,
        "fingerprint_count": fingerprint_count
    }


@router.delete("/{song_id}")
async def delete_upload(song_id: int, db: Session = Depends(get_db)):
    """Delete uploaded song and its file"""
    song = db.query(Song).filter(Song.id == song_id).first()
    
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    # Delete file from disk
    if song.file_path:
        from app.services.file_handler import delete_audio_file
        delete_audio_file(song.file_path)
    
    # Delete from database (fingerprints will cascade delete)
    db.delete(song)
    db.commit()
    
    return {"message": f"Song '{song.title}' deleted successfully"}
