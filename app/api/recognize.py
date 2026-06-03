from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Song, Fingerprint
from app.services.fingerprint import fingerprint_audio, match_fingerprints
from app.services.file_handler import validate_audio_file, save_audio_file
from app.services.visualize import generate_comparison_visualization
from typing import List, Dict
import os
import tempfile

router = APIRouter(prefix="/recognize", tags=["recognition"])


@router.post("/")
async def recognize_song(
    file: UploadFile = File(..., description="Audio clip to recognize (5-30 seconds recommended)"),
    db: Session = Depends(get_db)
):
    """
    Recognize a song from an audio clip
    
    Upload a short audio clip (5-30 seconds) and the system will:
    1. Generate fingerprints from the clip
    2. Match against database
    3. Return best matches with confidence scores
    
    Returns list of matches sorted by confidence (highest first)
    """
    
    # Validate file
    await validate_audio_file(file)
    
    # Save to temporary file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"query_{file.filename}")
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        print(f"🎵 Recognizing audio clip: {file.filename}")
        
        # Generate fingerprints for query audio
        query_fingerprints = fingerprint_audio(temp_path)
        print(f"📊 Generated {len(query_fingerprints)} fingerprints from query")
        
        # Build database fingerprint dictionary
        db_fingerprints = {}
        all_fingerprints = db.query(Fingerprint).all()
        
        print(f"🔍 Searching through {len(all_fingerprints)} database fingerprints...")
        
        for fp in all_fingerprints:
            if fp.hash_value not in db_fingerprints:
                db_fingerprints[fp.hash_value] = []
            db_fingerprints[fp.hash_value].append((fp.song_id, fp.time_offset))
        
        # Match fingerprints
        matches = match_fingerprints(query_fingerprints, db_fingerprints)
        
        if not matches:
            return {
                "success": False,
                "message": "No matches found",
                "matches": []
            }
        
        # Get song details for matches
        results = []
        for song_id, match_data in sorted(matches.items(), key=lambda x: x[1]['confidence'], reverse=True)[:5]:
            song = db.query(Song).filter(Song.id == song_id).first()
            if song:
                results.append({
                    "song_id": song.id,
                    "title": song.title,
                    "artist": song.artist.name,
                    "confidence": min(match_data['confidence'] / len(query_fingerprints), 1.0) if len(query_fingerprints) > 0 else 0,
                    "matches": match_data['matches'],
                    "time_offset": match_data['avg_time_offset']
                })
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            "success": True,
            "message": f"Found {len(results)} potential matches",
            "query_fingerprints": len(query_fingerprints),
            "matches": results
        }
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")


@router.post("/with-visualization")
async def recognize_with_visualization(
    file: UploadFile = File(..., description="Audio clip to recognize"),
    db: Session = Depends(get_db)
):
    """
    Recognize song and return comparison visualization
    
    Same as /recognize but also generates side-by-side spectrogram comparison
    with the best match.
    """
    
    # Validate file
    await validate_audio_file(file)
    
    # Save to temporary file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"query_{file.filename}")
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        print(f"🎵 Recognizing audio clip: {file.filename}")
        
        # Generate fingerprints
        query_fingerprints = fingerprint_audio(temp_path)
        
        # Build database fingerprint dictionary
        db_fingerprints = {}
        all_fingerprints = db.query(Fingerprint).all()
        
        for fp in all_fingerprints:
            if fp.hash_value not in db_fingerprints:
                db_fingerprints[fp.hash_value] = []
            db_fingerprints[fp.hash_value].append((fp.song_id, fp.time_offset))
        
        # Match fingerprints
        matches = match_fingerprints(query_fingerprints, db_fingerprints)
        
        if not matches:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return {
                "success": False,
                "message": "No matches found",
                "matches": [],
                "visualization": None
            }
        
        # Get best match
        best_match_id = max(matches.items(), key=lambda x: x[1]['confidence'])[0]
        best_song = db.query(Song).filter(Song.id == best_match_id).first()
        
        # Generate visualization
        visualization = None
        if best_song and best_song.file_path:
            try:
                visualization = generate_comparison_visualization(
                    temp_path,
                    best_song.file_path
                )
            except Exception as viz_error:
                print(f"⚠️ Visualization error: {viz_error}")
        
        # Get all match details
        results = []
        for song_id, match_data in sorted(matches.items(), key=lambda x: x[1]['confidence'], reverse=True)[:5]:
            song = db.query(Song).filter(Song.id == song_id).first()
            if song:
                results.append({
                    "song_id": song.id,
                    "title": song.title,
                    "artist": song.artist.name,
                    "confidence": min(match_data['confidence'] / len(query_fingerprints), 1.0) if len(query_fingerprints) > 0 else 0,
                    "matches": match_data['matches'],
                    "time_offset": match_data['avg_time_offset']
                })
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return {
            "success": True,
            "message": f"Found {len(results)} potential matches",
            "query_fingerprints": len(query_fingerprints),
            "matches": results,
            "visualization": visualization,
            "best_match": {
                "title": best_song.title,
                "artist": best_song.artist.name
            } if best_song else None
        }
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")


@router.get("/stats")
async def get_recognition_stats(db: Session = Depends(get_db)):
    """
    Get statistics about the recognition database
    """
    total_songs = db.query(Song).count()
    processed_songs = db.query(Song).filter(Song.is_processed == True).count()
    total_fingerprints = db.query(Fingerprint).count()
    
    avg_fingerprints = total_fingerprints / processed_songs if processed_songs > 0 else 0
    
    return {
        "total_songs": total_songs,
        "processed_songs": processed_songs,
        "pending_songs": total_songs - processed_songs,
        "total_fingerprints": total_fingerprints,
        "avg_fingerprints_per_song": round(avg_fingerprints, 2),
        "ready_for_recognition": processed_songs > 0
    }
