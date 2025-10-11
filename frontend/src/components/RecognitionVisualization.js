import React, { useState, useEffect } from 'react';
import { X, Download, Maximize2, Music, Search } from 'lucide-react';
import './RecognitionVisualization.css';

const RecognitionVisualization = ({ isOpen, onClose, visualizationData, matchData }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && visualizationData) {
      setIsLoading(false);
    }
  }, [isOpen, visualizationData]);

  const handleDownload = () => {
    if (visualizationData?.image_url) {
      const link = document.createElement('a');
      link.href = visualizationData.image_url;
      link.download = `recognition_comparison_${Date.now()}.png`;
      link.click();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="recognition-modal-overlay" onClick={onClose}>
      <div className="recognition-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="recognition-modal-header">
          <div className="recognition-modal-title">
            <h3>
              <Search className="title-icon" />
              Recognition Comparison
            </h3>
            {matchData && (
              <p>
                Query vs <strong>{matchData.title}</strong> by {matchData.artist}
              </p>
            )}
          </div>
          <div className="recognition-modal-actions">
            <button
              className="btn btn-secondary"
              onClick={handleDownload}
              disabled={!visualizationData?.image_url}
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

        <div className="recognition-modal-body">
          {isLoading && (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Generating comparison visualization...</p>
            </div>
          )}

          {error && (
            <div className="error-container">
              <p className="error-message">{error}</p>
            </div>
          )}

          {visualizationData?.image_url && (
            <div className="recognition-visualization-container">
              <div className="visualization-header">
                <h4>Side-by-Side Spectrogram Comparison</h4>
                <p>Left: Your audio clip | Right: Matched song</p>
              </div>
              <img
                src={visualizationData.image_url}
                alt="Recognition comparison visualization"
                className="recognition-image"
              />
              {visualizationData.description && (
                <div className="visualization-info">
                  <p>{visualizationData.description}</p>
                </div>
              )}
            </div>
          )}

          {!visualizationData && !isLoading && !error && (
            <div className="no-visualization">
              <Music className="no-viz-icon" />
              <h4>No Visualization Available</h4>
              <p>The recognition didn't generate a comparison visualization.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecognitionVisualization;