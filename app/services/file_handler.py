import os
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import uuid

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./media"))

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def validate_audio_file(file: UploadFile) -> dict:
    """
    Validate uploaded audio file
    Returns: dict with file info (duration, format, etc.)
    """
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)} MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    # Reset file pointer for later use
    await file.seek(0)
    
    return {
        "size": file_size,
        "extension": file_ext,
        "original_filename": file.filename
    }


async def save_audio_file(file: UploadFile, song_id: int) -> tuple[str, dict]:
    """
    Save uploaded file to disk and extract metadata
    Returns: (file_path, metadata_dict)
    """
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"song_{song_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Extract audio metadata
    try:
        audio = MutagenFile(str(file_path))
        
        if audio is None:
            raise HTTPException(status_code=400, detail="Could not read audio file")
        
        duration = audio.info.length if hasattr(audio.info, 'length') else None
        bitrate = audio.info.bitrate if hasattr(audio.info, 'bitrate') else None
        sample_rate = audio.info.sample_rate if hasattr(audio.info, 'sample_rate') else None
        
        metadata = {
            "duration": duration,
            "bitrate": bitrate,
            "sample_rate": sample_rate,
            "format": file_ext.replace('.', '').upper()
        }
        
    except Exception as e:
        # Clean up file if metadata extraction fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=400, detail=f"Invalid audio file: {str(e)}")
    
    return str(file_path), metadata


def delete_audio_file(file_path: str) -> bool:
    """Delete audio file from disk"""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False


def get_file_info(file_path: str) -> dict:
    """Get information about an audio file"""
    path = Path(file_path)
    
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        audio = MutagenFile(str(path))
        
        return {
            "filename": path.name,
            "size": path.stat().st_size,
            "duration": audio.info.length if audio and hasattr(audio.info, 'length') else None,
            "format": path.suffix.replace('.', '').upper()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
