from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Artist
from app.schemas.schemas import ArtistCreate, ArtistResponse

router = APIRouter(prefix="/artists", tags=["artists"])

@router.post("/", response_model=ArtistResponse, status_code=201)
def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
    """Create a new artist"""
    # Check if artist already exists
    existing = db.query(Artist).filter(Artist.name == artist.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Artist already exists")
    
    db_artist = Artist(name=artist.name)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

@router.get("/", response_model=List[ArtistResponse])
def get_artists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all artists"""
    artists = db.query(Artist).offset(skip).limit(limit).all()
    return artists

@router.get("/{artist_id}", response_model=ArtistResponse)
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    """Get artist by ID"""
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist

@router.delete("/{artist_id}")
def delete_artist(artist_id: int, db: Session = Depends(get_db)):
    """Delete an artist"""
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    
    db.delete(artist)
    db.commit()
    return {"message": "Artist deleted successfully"}
