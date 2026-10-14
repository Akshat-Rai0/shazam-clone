# Render Deployment Instructions

This document provides step-by-step instructions for deploying the Shazam Clone to Render with 5 test songs.

## Prerequisites

- Docker and Docker Compose installed locally
- A Render account (free tier is sufficient)
- 5 audio files (MP3 or WAV format) for testing

## Step 1: Prepare Test Songs

1. Create the `test_songs/` directory (already created)
2. Place 5 audio files in the directory:
   ```
   test_songs/
   ├── song1.mp3
   ├── song2.mp3
   ├── song3.mp3
   ├── song4.mp3
   └── song5.mp3
   ```

**File Requirements:**
- Format: MP3 or WAV
- Duration: 1-2 minutes preferred (shorter = faster processing)
- Size: <5MB each
- Content: Public domain or royalty-free music

## Step 2: Generate Fingerprints Locally

Since Render's free tier has a 60-second timeout, we'll generate fingerprints locally:

1. Start the local database:
   ```bash
   docker-compose up -d db
   ```

2. Run the fingerprint generation script:
   ```bash
   python scripts/generate_fingerprints.py
   ```

This script will:
- Create 3 test artists
- Process each audio file
- Generate fingerprints
- Export the database to `seed_data.sql`

3. Verify the `seed_data.sql` file was created and contains data

4. Stop the local database:
   ```bash
   docker-compose down
   ```

## Step 3: Commit Changes

1. Review the generated `seed_data.sql` file
2. Commit the changes to git:
   ```bash
   git add seed_data.sql scripts/ render-start.sh render.yaml .env.example frontend/.env.production.example
   git add app/core/database.py app/main.py Dockerfile
   git add frontend/src/pages/Upload.js frontend/src/pages/Upload.css frontend/src/services/api.js
   git add .gitignore
   git commit -m "Prepare for Render deployment"
   git push
   ```

**Note:** The `test_songs/` directory is in `.gitignore`, so audio files won't be committed.

## Step 4: Deploy to Render

### Option A: Using Render Dashboard (Recommended for first deployment)

1. **Create PostgreSQL Database:**
   - Go to https://dashboard.render.com/new/psql
   - Name: `shazam-clone-db`
   - Database: `shazam_db`
   - Plan: Free
   - Region: Oregon (or closest to you)
   - Click "Create Database"

2. **Create Backend Web Service:**
   - Go to https://dashboard.render.com/new/web
   - Name: `shazam-clone-api`
   - Runtime: Docker
   - Dockerfile path: `./Dockerfile`
   - Plan: Free
   - Region: Same as database
   - Environment Variables:
     - `DATABASE_URL`: Copy from database instance (click "Internal Database" on database page)
     - `UPLOAD_DIR`: `/tmp`
     - `PORT`: `8000`
   - Click "Create Web Service"

3. **Create Frontend Static Site:**
   - Go to https://dashboard.render.com/new/static
   - Name: `shazam-clone-frontend`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/build`
   - Plan: Free
   - Region: Same as other services
   - Environment Variables:
     - `REACT_APP_API_URL`: Copy from backend service URL (e.g., `https://shazam-clone-api.onrender.com`)
   - Click "Create Static Site"

### Option B: Using Render Blueprint (Advanced)

1. Install Render CLI:
   ```bash
   npm install -g @render/render-cli
   ```

2. Authenticate:
   ```bash
   render login
   ```

3. Validate blueprint:
   ```bash
   render blueprint validate render.yaml
   ```

4. Apply blueprint:
   ```bash
   render blueprint apply render.yaml
   ```

## Step 5: Verify Deployment

1. **Check Backend Health:**
   - Visit: `https://shazam-clone-api.onrender.com/health`
   - Should return: `{"status": "healthy", ...}`

2. **Check API Documentation:**
   - Visit: `https://shazam-clone-api.onrender.com/docs`
   - Should show FastAPI documentation

3. **Check Frontend:**
   - Visit: `https://shazam-clone-frontend.onrender.com`
   - Should load the React application

4. **Verify Database Seeding:**
   - Visit: `https://shazam-clone-api.onrender.com/songs/`
   - Should show 5 songs with `is_processed: true`

5. **Test Recognition:**
   - Go to the Home page
   - Upload a short audio clip from one of the test songs
   - Should recognize the song

## Troubleshooting

### Backend fails to start
- Check the Render logs for the backend service
- Ensure DATABASE_URL is correctly formatted
- Verify the database is accessible

### Frontend can't connect to backend
- Check that REACT_APP_API_URL is set correctly
- Verify CORS settings in `app/main.py`
- Check browser console for errors

### Database not seeded
- Check that `seed_data.sql` was committed to the repo
- Review the startup logs in Render
- Manually trigger a redeploy if needed

### Audio recognition not working
- Verify songs have fingerprints (check `/songs/` endpoint)
- Ensure the audio clip is from one of the test songs
- Check the recognition logs in Render

## Free Tier Limitations

Render's free tier has these limitations:
- Services sleep after 15 minutes of inactivity
- First request after sleep may have a delay (cold start)
- 60-second timeout for builds
- 512MB RAM (may be insufficient for heavy processing)

For production use, consider upgrading to the Starter plan ($7/mo) for:
- Always-on services
- More RAM and CPU
- Longer timeouts
- Better performance

## Environment Variables

### Backend
- `DATABASE_URL`: Provided by Render Postgres instance
- `UPLOAD_DIR`: `/tmp` (temporary storage)
- `PORT`: `8000`

### Frontend
- `REACT_APP_API_URL`: Backend service URL

## File Structure After Deployment

```
shazam-clone/
├── test_songs/              # Local only (not committed)
│   ├── song1.mp3
│   ├── song2.mp3
│   └── ...
├── scripts/
│   ├── generate_fingerprints.py  # Local fingerprint generation
│   └── seed_database.py          # Render seeding script
├── seed_data.sql            # Committed (pre-generated fingerprints)
├── render-start.sh         # Render startup script
├── render.yaml             # Render blueprint
├── .env.example            # Environment variable template
└── frontend/
    └── .env.production.example  # Frontend env var template
```

## Next Steps

After successful deployment:
1. Test the recognition feature with various audio clips
2. Monitor the Render logs for any issues
3. Consider upgrading to paid tier if needed for production
4. Add more test songs if desired (repeat Step 2)
