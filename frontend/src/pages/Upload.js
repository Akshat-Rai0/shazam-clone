import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload as UploadIcon, Plus, Music, User } from 'lucide-react';
import { uploadSong, getArtists, createArtist } from '../services/api';
import './Upload.css';

const Upload = ({ isLoading, setIsLoading }) => {
  const [artists, setArtists] = useState([]);
  const [selectedArtist, setSelectedArtist] = useState('');
  const [songTitle, setSongTitle] = useState('');
  const [newArtistName, setNewArtistName] = useState('');
  const [showNewArtistForm, setShowNewArtistForm] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  // Load artists on component mount
  React.useEffect(() => {
    loadArtists();
  }, []);

  const loadArtists = async () => {
    try {
      const artistsData = await getArtists();
      setArtists(artistsData);
    } catch (err) {
      setError('Failed to load artists');
    }
  };

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setIsLoading(true);
    setError(null);
    setUploadResult(null);

    try {
      if (!selectedArtist && !newArtistName) {
        throw new Error('Please select an artist or create a new one');
      }

      let artistId = selectedArtist;
      
      // Create new artist if needed
      if (newArtistName && !selectedArtist) {
        const newArtist = await createArtist(newArtistName);
        artistId = newArtist.id;
        setArtists(prev => [...prev, newArtist]);
        setSelectedArtist(artistId);
      }

      const response = await uploadSong(file, songTitle, artistId);
      setUploadResult(response);
      setSongTitle('');
      setSelectedArtist('');
      setNewArtistName('');
      setShowNewArtistForm(false);
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  }, [selectedArtist, newArtistName, songTitle, setIsLoading]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a', '.flac', '.aac']
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  const handleCreateArtist = async (e) => {
    e.preventDefault();
    if (!newArtistName.trim()) return;

    try {
      const newArtist = await createArtist(newArtistName.trim());
      setArtists(prev => [...prev, newArtist]);
      setSelectedArtist(newArtist.id);
      setNewArtistName('');
      setShowNewArtistForm(false);
    } catch (err) {
      setError(err.message || 'Failed to create artist');
    }
  };

  return (
    <div className="upload">
      <div className="upload-header">
        <h1 className="upload-title">
          <UploadIcon className="upload-icon" />
          Upload Songs
        </h1>
        <p className="upload-subtitle">
          Add new songs to the recognition database
        </p>
      </div>

      <div className="upload-content">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Song Information</h2>
            <p className="card-subtitle">
              Provide song details before uploading
            </p>
          </div>

          <form className="upload-form">
            <div className="form-group">
              <label className="form-label">Song Title</label>
              <input
                type="text"
                className="form-input"
                value={songTitle}
                onChange={(e) => setSongTitle(e.target.value)}
                placeholder="Enter song title"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Artist</label>
              <div className="artist-selection">
                <select
                  className="form-select"
                  value={selectedArtist}
                  onChange={(e) => {
                    setSelectedArtist(e.target.value);
                    setShowNewArtistForm(false);
                  }}
                  disabled={showNewArtistForm}
                >
                  <option value="">Select an artist</option>
                  {artists.map(artist => (
                    <option key={artist.id} value={artist.id}>
                      {artist.name}
                    </option>
                  ))}
                </select>
                
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowNewArtistForm(!showNewArtistForm)}
                >
                  <Plus className="btn-icon" />
                  {showNewArtistForm ? 'Cancel' : 'New Artist'}
                </button>
              </div>

              {showNewArtistForm && (
                <form onSubmit={handleCreateArtist} className="new-artist-form">
                  <div className="form-group">
                    <label className="form-label">New Artist Name</label>
                    <div className="new-artist-input">
                      <input
                        type="text"
                        className="form-input"
                        value={newArtistName}
                        onChange={(e) => setNewArtistName(e.target.value)}
                        placeholder="Enter artist name"
                        required
                      />
                      <button type="submit" className="btn btn-primary">
                        <User className="btn-icon" />
                        Create
                      </button>
                    </div>
                  </div>
                </form>
              )}
            </div>
          </form>

          <div className="upload-area">
            <div
              {...getRootProps()}
              className={`dropzone ${isDragActive ? 'active' : ''}`}
            >
              <input {...getInputProps()} />
              <Music className="dropzone-icon" />
              <div className="dropzone-text">
                {isDragActive ? 'Drop the audio file here' : 'Drag & drop audio file here'}
              </div>
              <div className="dropzone-subtext">
                or click to browse (MP3, WAV, M4A, FLAC, AAC)
              </div>
            </div>
          </div>

          {isLoading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Uploading and processing song... This may take a few minutes.</p>
            </div>
          )}

          {error && (
            <div className="error-container">
              <p className="error-message">{error}</p>
            </div>
          )}

          {uploadResult && (
            <div className="upload-result">
              <h3 className="result-title">Upload Successful!</h3>
              <div className="result-details">
                <p><strong>Song:</strong> {uploadResult.title}</p>
                <p><strong>Artist:</strong> {uploadResult.artist.name}</p>
                <p><strong>Duration:</strong> {uploadResult.duration}s</p>
                <p><strong>Status:</strong> {uploadResult.status}</p>
              </div>
              <p className="result-note">
                The song is being processed in the background. 
                Check the Library page to monitor processing status.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Upload;