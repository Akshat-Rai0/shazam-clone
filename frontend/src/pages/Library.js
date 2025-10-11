import React, { useState, useEffect } from 'react';
import { Library as LibraryIcon, Music, User, Clock, CheckCircle, AlertCircle, Eye } from 'lucide-react';
import { getSongs, getUploadStatus } from '../services/api';
import SpectrogramModal from '../components/SpectrogramModal';
import './Library.css';

const Library = ({ isLoading, setIsLoading }) => {
  const [songs, setSongs] = useState([]);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [selectedSong, setSelectedSong] = useState(null);
  const [showSpectrogram, setShowSpectrogram] = useState(false);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [songsData, statusData] = await Promise.all([
        getSongs(),
        getUploadStatus()
      ]);
      setSongs(songsData);
      setStatus(statusData);
    } catch (err) {
      setError(err.message || 'Failed to load library data');
    }
  };

  const getStatusIcon = (isProcessed) => {
    if (isProcessed) {
      return <CheckCircle className="status-icon success" />;
    }
    return <Clock className="status-icon processing" />;
  };

  const getStatusText = (isProcessed) => {
    return isProcessed ? 'Ready for recognition' : 'Processing...';
  };

  const handleSongClick = (song) => {
    setSelectedSong(song);
    setShowSpectrogram(true);
  };

  const handleCloseSpectrogram = () => {
    setShowSpectrogram(false);
    setSelectedSong(null);
  };

  return (
    <div className="library">
      <div className="library-header">
        <h1 className="library-title">
          <LibraryIcon className="library-icon" />
          Music Library
        </h1>
        <p className="library-subtitle">
          Manage your uploaded songs and track processing status
        </p>
      </div>

      {status && (
        <div className="status-overview">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">{status.total_songs}</div>
              <div className="stat-label">Total Songs</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{status.processed}</div>
              <div className="stat-label">Processed</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{status.pending}</div>
              <div className="stat-label">Pending</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">{status.progress_percent}%</div>
              <div className="stat-label">Progress</div>
            </div>
          </div>
        </div>
      )}

      <div className="library-content">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Songs</h2>
            <p className="card-subtitle">
              {songs.length} songs in library
            </p>
          </div>

          {error && (
            <div className="error-container">
              <p className="error-message">{error}</p>
            </div>
          )}

          {songs.length === 0 ? (
            <div className="empty-library">
              <Music className="empty-icon" />
              <h3>No songs uploaded yet</h3>
              <p>Upload some songs to start building your music library</p>
            </div>
          ) : (
            <div className="songs-list">
              {songs.map(song => (
                <div key={song.id} className="song-item">
                  <div className="song-info">
                    <div className="song-header">
                      <h4 
                        className="song-title clickable"
                        onClick={() => handleSongClick(song)}
                        title="Click to view spectrogram"
                      >
                        {song.title}
                        <Eye className="view-icon" />
                      </h4>
                      <div className="song-status">
                        {getStatusIcon(song.is_processed)}
                        <span className="status-text">
                          {getStatusText(song.is_processed)}
                        </span>
                      </div>
                    </div>
                    <div className="song-details">
                      <div className="song-artist">
                        <User className="detail-icon" />
                        <span>{song.artist.name}</span>
                      </div>
                      <div className="song-duration">
                        <Clock className="detail-icon" />
                        <span>{song.duration}s</span>
                      </div>
                      <div className="song-format">
                        <span className="format-badge">{song.file_format}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {selectedSong && (
        <SpectrogramModal
          isOpen={showSpectrogram}
          onClose={handleCloseSpectrogram}
          songId={selectedSong.id}
          songTitle={selectedSong.title}
          songArtist={selectedSong.artist.name}
        />
      )}
    </div>
  );
};

export default Library;