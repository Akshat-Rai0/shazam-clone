from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Song, Artist
from app.schemas.schemas import SongCreate, SongResponse

router = APIRouter(prefix="/songs", tags=["songs"])

@router.post("/", response_model=SongResponse, status_code=201)
def create_song(song: SongCreate, db: Session = Depends(get_db)):
    """Create a new song"""
    # Verify artist exists
    artist = db.query(Artist).filter(Artist.id == song.artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    db_song = Song(**song.dict())
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

@router.get("/", response_model=List[SongResponse])
def get_songs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all songs"""
    songs = db.query(Song).offset(skip).limit(limit).all()
    return songs

@router.get("/{song_id}", response_model=SongResponse)
def get_song(song_id: int, db: Session = Depends(get_db)):
    """Get song by ID"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.delete("/{song_id}")
def delete_song(song_id: int, db: Session = Depends(get_db)):
    """Delete a song"""
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    db.delete(song)
    db.commit()
    return {"message": "Song deleted successfully"}
