from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Song
from app.services.visualize import (
    generate_spectrogram_image,
    generate_peaks_visualization
)
from app.services.fingerprint import (
    load_audio,
    generate_spectrogram,
    find_peaks
)
import base64

router = APIRouter(prefix="/visualize", tags=["visualization"])


@router.get("/spectrogram/{song_id}")
async def get_spectrogram(
    song_id: int,
    show_peaks: bool = Query(False, description="Overlay detected peaks on spectrogram"),
    db: Session = Depends(get_db)
):
    """
    Get spectrogram visualization for a song
    
    - **song_id**: ID of the song
    - **show_peaks**: If True, show detected peaks overlaid on spectrogram
    """
    song = db.query(Song).filter(Song.id == song_id).first()
    
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if not song.file_path:
        raise HTTPException(status_code=404, detail="No audio file for this song")
    
    try:
        if show_peaks:
            # Generate spectrogram with peaks
            audio, sr = load_audio(song.file_path)
            spec = generate_spectrogram(audio)
            peaks = find_peaks(spec)
            
            img_base64 = generate_peaks_visualization(song.file_path, peaks)
        else:
            # Simple spectrogram
            img_base64 = generate_spectrogram_image(song.file_path)
        
        # Return HTML page with embedded image
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spectrogram - {song.title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                }}
                h1 {{
                    color: #333;
                    margin-bottom: 10px;
                }}
                .info {{
                    color: #666;
                    margin-bottom: 30px;
                    font-size: 14px;
                }}
                .info span {{
                    background: #f0f0f0;
                    padding: 5px 10px;
                    border-radius: 5px;
                    margin-right: 10px;
                }}
                img {{
                    width: 100%;
                    border-radius: 10px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                }}
                .back-link {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background 0.3s;
                }}
                .back-link:hover {{
                    background: #764ba2;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎵 {song.title}</h1>
                <div class="info">
                    <span>Artist: {song.artist.name}</span>
                    <span>Duration: {song.duration:.1f}s</span>
                    <span>Processed: {"✅ Yes" if song.is_processed else "⏳ Processing..."}</span>
                    {f'<span>Peaks: {len(peaks) if show_peaks else "N/A"}</span>' if show_peaks else ''}
                </div>
                <img src="{img_base64}" alt="Spectrogram">
                <br>
                <a href="/docs" class="back-link">← Back to API Docs</a>
                {f'<a href="/visualize/spectrogram/{song_id}" class="back-link">View without peaks</a>' if show_peaks else f'<a href="/visualize/spectrogram/{song_id}?show_peaks=true" class="back-link">View with peaks</a>'}
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating visualization: {str(e)}")


@router.get("/api/spectrogram/{song_id}")
async def get_spectrogram_json(
    song_id: int,
    show_peaks: bool = Query(False, description="Overlay detected peaks on spectrogram"),
    db: Session = Depends(get_db)
):
    """
    Get spectrogram visualization for a song as JSON data
    
    - **song_id**: ID of the song
    - **show_peaks**: If True, show detected peaks overlaid on spectrogram
    """
    song = db.query(Song).filter(Song.id == song_id).first()
    
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if not song.file_path:
        raise HTTPException(status_code=404, detail="No audio file for this song")
    
    try:
        if show_peaks:
            # Generate spectrogram with peaks
            audio, sr = load_audio(song.file_path)
            spec = generate_spectrogram(audio)
            peaks = find_peaks(spec)
            
            img_base64 = generate_peaks_visualization(song.file_path, peaks)
            description = f"Spectrogram with {len(peaks)} detected peaks overlaid"
        else:
            # Simple spectrogram
            img_base64 = generate_spectrogram_image(song.file_path)
            description = "Standard spectrogram visualization"
        
        return {
            "success": True,
            "song_id": song.id,
            "title": song.title,
            "artist": song.artist.name,
            "duration": song.duration,
            "is_processed": song.is_processed,
            "show_peaks": show_peaks,
            "image_url": f"data:image/png;base64,{img_base64}",
            "description": description,
            "peaks_count": len(peaks) if show_peaks else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating visualization: {str(e)}")


@router.get("/all")
async def list_visualizations(db: Session = Depends(get_db)):
    """List all songs available for visualization"""
    songs = db.query(Song).filter(Song.file_path.isnot(None)).all()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Song Visualizations</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }
            h1 {
                color: #333;
            }
            .song-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .song-card {
                border: 1px solid #ddd;
                padding: 20px;
                border-radius: 10px;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .song-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            }
            .song-title {
                font-size: 18px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
            .song-artist {
                color: #666;
                margin-bottom: 15px;
            }
            .btn {
                display: inline-block;
                padding: 8px 15px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-right: 10px;
                font-size: 14px;
            }
            .btn:hover {
                background: #764ba2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 Song Visualizations</h1>
            <p>Click on any song to view its spectrogram</p>
            <div class="song-grid">
    """
    
    for song in songs:
        html_content += f"""
                <div class="song-card">
                    <div class="song-title">{song.title}</div>
                    <div class="song-artist">by {song.artist.name}</div>
                    <a href="/visualize/spectrogram/{song.id}" class="btn">View Spectrogram</a>
                    <a href="/visualize/spectrogram/{song.id}?show_peaks=true" class="btn">With Peaks</a>
                </div>
        """
    
    html_content += """
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
