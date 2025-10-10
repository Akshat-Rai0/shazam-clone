
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    songs = relationship("Song", back_populates="artist", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Artist(id={self.id}, name={self.name})>"


class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)
    duration = Column(Float, nullable=True)  # Duration in seconds
    file_path = Column(String(500), nullable=True)  # Path to audio file
    file_format = Column(String(10), nullable=True)  # mp3, wav, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    is_processed = Column(Boolean, default=False)  # Track if fingerprinting is done
    
    # Relationships
    artist = relationship("Artist", back_populates="songs")
    fingerprints = relationship("Fingerprint", back_populates="song", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Song(id={self.id}, title={self.title}, artist={self.artist.name if self.artist else 'Unknown'})>"


class Fingerprint(Base):
    __tablename__ = "fingerprints"
    
    id = Column(Integer, primary_key=True, index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    hash_value = Column(String(255), nullable=False, index=True)  # Audio fingerprint hash
    time_offset = Column(Float, nullable=False)  # Time offset in the song (seconds)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    song = relationship("Song", back_populates="fingerprints")
    
    def __repr__(self):
        return f"<Fingerprint(id={self.id}, song_id={self.song_id}, hash={self.hash_value[:10]}...)>"
