# 🎵 Shazam Clone - Audio Recognition System

A full-stack audio fingerprinting and recognition system inspired by Shazam, built with FastAPI, PostgreSQL, and advanced signal processing algorithms.

## 🚀 Features

- **Audio Fingerprinting**: Generate unique acoustic fingerprints using spectrogram peak analysis
- **Song Recognition**: Match audio clips against a database of songs with confidence scoring
- **Real-time Processing**: Background task processing for handling large audio files
- **Visualization**: View spectrograms and detected peaks for any uploaded song
- **RESTful API**: Complete CRUD operations for artists, songs, and recognition

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Audio Processing**: librosa, scipy, numpy
- **Visualization**: matplotlib
- **Containerization**: Docker & Docker Compose
- **Migrations**: Alembic

## 📋 Prerequisites

- Docker & Docker Compose
- 4GB RAM minimum (for audio processing)
- 2GB free disk space

## 🏃 Quick Start

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd shazam-clone
```

2. **Create `.env` file** (see Configuration section below)

3. **Start the application**
```bash
docker-compose up --build
```

4. **Access the API**
- API Documentation: http://localhost:8000/docs
- Interactive UI: http://localhost:8000/visualize/all
- Health Check: http://localhost:8000/health

## ⚙️ Configuration

Create a `.env` file in the root directory:

```bash
# Database
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=shazam_db
DATABASE_URL=postgresql://user:password@db:5432/shazam_db

# Upload
UPLOAD_DIR=/app/media
```

## 📚 API Usage

### 1. Create an Artist
```bash
curl -X POST "http://localhost:8000/artists/" \
  -H "Content-Type: application/json" \
  -d '{"name": "The Beatles"}'
```

### 2. Upload a Song
```bash
curl -X POST "http://localhost:8000/upload/" \
  -F "file=@song.mp3" \
  -F "title=Hey Jude" \
  -F "artist_id=1"
```

### 3. Recognize Audio Clip
```bash
curl -X POST "http://localhost:8000/recognize/" \
  -F "file=@query.mp3"
```

**Response:**
```json
{
  "success": true,
  "message": "Found 3 potential matches",
  "query_fingerprints": 1247,
  "matches": [
    {
      "song_id": 1,
      "title": "Hey Jude",
      "artist": "The Beatles",
      "confidence": 45.32,
      "matches": 234,
      "time_offset": 12.5
    }
  ]
}
```

### 4. View Statistics
```bash
curl "http://localhost:8000/recognize/stats"
```

## 🎯 How It Works

### Audio Fingerprinting Algorithm

1. **Audio Loading**: Convert audio to mono, resample to 22kHz
2. **Spectrogram Generation**: Apply STFT (Short-Time Fourier Transform) with 4096 FFT window
3. **Peak Detection**: Find local maxima in the frequency-time domain
4. **Hash Generation**: Create combinatorial hashes from peak pairs (freq1, freq2, time_delta)
5. **Storage**: Store hashes with time offsets in PostgreSQL

### Recognition Process

1. **Query Processing**: Generate fingerprints from audio clip
2. **Hash Matching**: Compare query hashes against database
3. **Time Consistency**: Calculate time offset consistency for matches
4. **Confidence Scoring**: Score matches based on count and time alignment
5. **Ranking**: Return top matches sorted by confidence

## 📁 Project Structure

```
shazam-clone/
├── app/
│   ├── api/              # API route handlers
│   │   ├── artists.py
│   │   ├── songs.py
│   │   ├── upload.py
│   │   ├── recognize.py
│   │   └── visualize.py
│   ├── core/             # Core configurations
│   │   └── database.py
│   ├── models/           # SQLAlchemy models
│   │   └── models.py
│   ├── schemas/          # Pydantic schemas
│   │   └── schemas.py
│   ├── services/         # Business logic
│   │   ├── fingerprint.py   # Audio fingerprinting
│   │   ├── file_handler.py  # File operations
│   │   └── visualize.py     # Spectrogram generation
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
├── media/                # Uploaded audio files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

## 🔬 Algorithm Parameters

```python
SAMPLE_RATE = 22050              # Audio sample rate
FFT_WINDOW_SIZE = 4096           # Spectrogram window size
OVERLAP_RATIO = 0.5              # Window overlap
FAN_VALUE = 5                    # Hash fan-out factor
PEAK_NEIGHBORHOOD_SIZE = 10      # Peak detection window
MIN_AMPLITUDE = 10               # Minimum peak amplitude
MAX_HASH_TIME_DELTA = 200        # Maximum time between peaks
```

## 📊 Database Schema

**Artists** → **Songs** → **Fingerprints**

- Artists: id, name, created_at
- Songs: id, title, artist_id, duration, file_path, is_processed
- Fingerprints: id, song_id, hash_value (indexed), time_offset

## 🎨 Visualization

View spectrograms and detected peaks:
- All songs: http://localhost:8000/visualize/all
- Specific song: http://localhost:8000/visualize/spectrogram/{song_id}
- With peaks: http://localhost:8000/visualize/spectrogram/{song_id}?show_peaks=true

## 🧪 Testing the System

1. Upload 3-5 songs (full tracks)
2. Wait for processing to complete (check `/upload/status`)
3. Record a 10-15 second clip from one of the songs
4. Use `/recognize/` endpoint to identify the clip
5. View visualization with `/recognize/with-visualization`

## 🚧 Known Limitations

- Recognition accuracy depends on audio quality (bitrate, noise)
- Best results with clips 10-30 seconds long
- Processing time: ~30-60 seconds per song
- No real-time streaming recognition

## 🔮 Future Enhancements

- [ ] Add frontend UI for easier interaction
- [ ] Implement WebSocket for real-time processing updates
- [ ] Add support for more audio formats (AAC, OGG)
- [ ] Optimize fingerprinting for faster processing
- [ ] Add batch upload functionality
- [ ] Implement caching for frequently queried songs

## 📝 License

MIT License - feel free to use for learning and projects

## 👤 Author

Your Name - Akshat Rai [GitHub](https://github.com/Akshat699) | [LinkedIn](https://www.linkedin.com/in/akshat-rai-196497339/)
            Shashwat Saurav [Github](https://github.com/shashwatsrv) | [LinkedIn](https://www.linkedin.com/in/shashwat-saurav-4a0a60276/)

## 🙏 Acknowledgments

- Inspired by the paper: "An Industrial-Strength Audio Search Algorithm" (Wang, 2003)
- Built with FastAPI and librosa