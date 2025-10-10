from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from app.api import artists, songs, upload, visualize, recognize
from app.core.database import engine, Base
import traceback

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shazam Clone API",
    description="""
    🎵 Audio Recognition System with Fingerprinting
    
    This API provides:
    - Audio fingerprinting using spectrogram analysis
    - Song recognition from audio clips
    - Spectrogram visualization
    - Complete artist and song management
    
    ## How to Use
    1. Create an artist using `/artists/`
    2. Upload songs using `/upload/`
    3. Wait for processing (check `/upload/status`)
    4. Recognize audio with `/recognize/`
    """,
    version="1.0.0",
    contact={
        "name": "Your Name",
        "url": "https://github.com/yourusername",
    },
    license_info={
        "name": "MIT",
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler for unhandled errors.
    Returns a consistent error response format.
    """
    print(f"❌ Unhandled exception: {str(exc)}")
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )


# Include routers
app.include_router(artists.router)
app.include_router(songs.router)
app.include_router(upload.router)
app.include_router(visualize.router)
app.include_router(recognize.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information and quick links.
    """
    return {
        "message": "🎵 Shazam Clone API - Audio Recognition System",
        "version": "1.0.0",
        "status": "running",
        "description": "Upload songs, generate fingerprints, and recognize audio clips",
        "quick_links": {
            "📖 API Documentation": "/docs",
            "🏥 Health Check": "/health",
            "👨‍🎤 Manage Artists": "/artists",
            "🎵 Manage Songs": "/songs",
            "📤 Upload Songs": "/upload",
            "🔍 Recognize Audio": "/recognize",
            "📊 View Spectrograms": "/visualize/all",
            "📈 Recognition Stats": "/recognize/stats"
        },
        "quick_start": {
            "1": "Create an artist: POST /artists/",
            "2": "Upload a song: POST /upload/",
            "3": "Check processing: GET /upload/status",
            "4": "Recognize clip: POST /recognize/"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and container orchestration.
    Returns service status and database connectivity.
    """
    from app.core.database import engine
    
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "shazam-clone-api",
        "version": "1.0.0",
        "database": db_status
    }


@app.on_event("startup")
async def startup_event():
    """Runs when the application starts"""
    print("\n" + "=" * 70)
    print("🚀 Shazam Clone API - Starting Up")
    print("=" * 70)
    print(f"⏰ Started at: {datetime.utcnow().isoformat()}")
    print("\n📍 Endpoints:")
    print("   📖 API Documentation:    http://localhost:8000/docs")
    print("   🏥 Health Check:         http://localhost:8000/health")
    print("   👨‍🎤 Artists:              http://localhost:8000/artists")
    print("   🎵 Songs:                http://localhost:8000/songs")
    print("   📤 Upload:               http://localhost:8000/upload")
    print("   🔍 Recognize:            http://localhost:8000/recognize")
    print("   📊 Visualizations:       http://localhost:8000/visualize/all")
    print("   📈 Stats:                http://localhost:8000/recognize/stats")
    print("=" * 70 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the application shuts down"""
    print("\n" + "=" * 70)
    print("👋 Shazam Clone API - Shutting Down")
    print(f"⏰ Stopped at: {datetime.utcnow().isoformat()}")
    print("=" * 70 + "\n")