
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Artist Schemas
class ArtistBase(BaseModel):
    name: str

class ArtistCreate(ArtistBase):
    pass

class ArtistResponse(ArtistBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Song Schemas
class SongBase(BaseModel):
    title: str
    artist_id: int
    duration: Optional[float] = None
    file_format: Optional[str] = None

class SongCreate(SongBase):
    pass

class SongResponse(SongBase):
    id: int
    file_path: Optional[str] = None
    created_at: datetime
    is_processed: bool
    artist: Optional[ArtistResponse] = None
    
    class Config:
        from_attributes = True

# Fingerprint Schemas
class FingerprintBase(BaseModel):
    song_id: int
    hash_value: str
    time_offset: float

class FingerprintCreate(FingerprintBase):
    pass

class FingerprintResponse(FingerprintBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Response with list of songs
class SongListResponse(BaseModel):
    songs: List[SongResponse]
    total: int
