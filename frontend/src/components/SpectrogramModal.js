import React, { useState, useEffect } from 'react';
import { X, Download, Maximize2, RotateCcw } from 'lucide-react';
import { getSongVisualization } from '../services/api';
import './SpectrogramModal.css';

const SpectrogramModal = ({ isOpen, onClose, songId, songTitle, songArtist }) => {
  const [spectrogramData, setSpectrogramData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showPeaks, setShowPeaks] = useState(false);

  useEffect(() => {
    if (isOpen && songId) {
      loadSpectrogram();
    }
  }, [isOpen, songId]);

  const loadSpectrogram = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await getSongVisualization(songId, showPeaks);
      setSpectrogramData(data);
    } catch (err) {
      setError(err.message || 'Failed to load spectrogram');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTogglePeaks = () => {
    setShowPeaks(!showPeaks);
    loadSpectrogram();
  };

  const handleDownload = () => {
    if (spectrogramData?.image_url) {
      const link = document.createElement('a');
      link.href = spectrogramData.image_url;
      link.download = `${songTitle}_spectrogram.png`;
      link.click();
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