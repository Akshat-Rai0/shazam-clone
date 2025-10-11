import React, { useState, useEffect, useCallback } from 'react';
import { X, Download, RotateCcw } from 'lucide-react';
import { getSongVisualization } from '../services/api';
import './SpectrogramModal.css';

const SpectrogramModal = ({ isOpen, onClose, songId, songTitle, songArtist }) => {
  const [spectrogramData, setSpectrogramData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showPeaks, setShowPeaks] = useState(false);

  const loadSpectrogram = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Loading spectrogram for song:', songId, 'showPeaks:', showPeaks);
      const data = await getSongVisualization(songId, showPeaks);
      console.log('Spectrogram data received:', data);
      setSpectrogramData(data);
    } catch (err) {
      console.error('Error loading spectrogram:', err);
      setError(err.message || 'Failed to load spectrogram');
    } finally {
      setIsLoading(false);
    }
  }, [songId, showPeaks]);

  useEffect(() => {
    if (isOpen && songId) {
      loadSpectrogram();
    }
  }, [isOpen, songId, loadSpectrogram]);

  const handleTogglePeaks = () => {
    setShowPeaks(!showPeaks);
    loadSpectrogram();
  };

  const handleDownload = () => {
    if (spectrogramData?.image_url) {
      console.log('Downloading spectrogram:', spectrogramData.image_url.substring(0, 50) + '...');
      const link = document.createElement('a');
      link.href = spectrogramData.image_url;
      link.download = `${songTitle}_spectrogram.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      console.error('No image URL available for download');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <h3>Spectrogram: {songTitle}</h3>
            <p>by {songArtist}</p>
          </div>
          <div className="modal-actions">
            <button
              className="btn btn-secondary"
              onClick={handleTogglePeaks}
              disabled={isLoading}
            >
              <RotateCcw className="btn-icon" />
              {showPeaks ? 'Hide Peaks' : 'Show Peaks'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleDownload}
              disabled={!spectrogramData?.image_url}
            >
              <Download className="btn-icon" />
              Download
            </button>
            <button className="btn btn-secondary" onClick={onClose}>
              <X className="btn-icon" />
              Close
            </button>
          </div>
        </div>

        <div className="modal-body">
          {isLoading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Generating spectrogram...</p>
            </div>
          )}

          {error && (
            <div className="error-container">
              <p className="error-message">{error}</p>
            </div>
          )}

          {spectrogramData?.image_url && (
            <div className="spectrogram-container">
              <img
                src={spectrogramData.image_url}
                alt={`Spectrogram for ${songTitle}`}
                className="spectrogram-image"
                onLoad={() => console.log('Spectrogram image loaded successfully')}
                onError={(e) => console.error('Error loading spectrogram image:', e)}
              />
              {spectrogramData.description && (
                <div className="spectrogram-info">
                  <p>{spectrogramData.description}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SpectrogramModal;