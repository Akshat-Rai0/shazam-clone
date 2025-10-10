from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.api import artists, songs, upload, visualize, recognize
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shazam Clone API",
    description="Audio recognition system with fingerprinting and visualization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(artists.router)
app.include_router(songs.router)
app.include_router(upload.router)
app.include_router(visualize.router)
app.include_router(recognize.router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🎵 Shazam Clone API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "artists": "/artists",
            "songs": "/songs",
            "upload": "/upload",
            "recognize": "/recognize",
            "visualize": "/visualize/all",
            "stats": "/recognize/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "shazam-clone-api",
        "database": "connected"
    }

@app.on_event("startup")
async def startup_event():
    """Runs when the application starts"""
    print("=" * 60)
    print("🚀 Shazam Clone API starting up...")
    print("=" * 60)
    print("📝 API Documentation:    http://localhost:8000/docs")
    print("🎵 Artists:              http://localhost:8000/artists")
    print("🎶 Songs:                http://localhost:8000/songs")
    print("📤 Upload:               http://localhost:8000/upload")
    print("🔍 Recognize:            http://localhost:8000/recognize")
    print("📊 Visualizations:       http://localhost:8000/visualize/all")
    print("📈 Stats:                http://localhost:8000/recognize/stats")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the application shuts down"""
    print("👋 Shazam Clone API shutting down...")
