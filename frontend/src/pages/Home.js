import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Music, Search, Eye } from 'lucide-react';
import { recognizeAudio, recognizeWithVisualization } from '../services/api';
import RecognitionVisualization from '../components/RecognitionVisualization';
import './Home.css';

const Home = ({ isLoading, setIsLoading }) => {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [showVisualization, setShowVisualization] = useState(false);
  const [visualizationData, setVisualizationData] = useState(null);
  const [selectedMatch, setSelectedMatch] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await recognizeAudio(file);
      setResults(response);
      setVisualizationData(null);
      setShowVisualization(false);
    } catch (err) {
      setError(err.message || 'Recognition failed');
    } finally {
      setIsLoading(false);
    }
  }, [setIsLoading]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a', '.flac', '.aac']
    },
    multiple: false,
    maxSize: 50 * 1024 * 1024 // 50MB
  });


  const handleViewVisualization = async (match) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Create a temporary file input to get the original file
      const fileInput = document.querySelector('input[type="file"]');
      if (!fileInput || !fileInput.files[0]) {
        throw new Error('Original audio file not found');
      }
      
      const response = await recognizeWithVisualization(fileInput.files[0]);
      setVisualizationData(response.visualization);
      setSelectedMatch(match);
      setShowVisualization(true);
    } catch (err) {
      setError(err.message || 'Failed to generate visualization');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCloseVisualization = () => {
    setShowVisualization(false);
    setVisualizationData(null);
    setSelectedMatch(null);
  };

  return (
    <div className="home">
      <div className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            <Music className="hero-icon" />
            Recognize Any Song
          </h1>
          <p className="hero-subtitle">
            Upload an audio clip or record a snippet to identify any song instantly
          </p>
        </div>
      </div>

      <div className="recognition-section">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Audio Recognition</h2>
            <p className="card-subtitle">
              Upload a 5-30 second audio clip to identify the song
            </p>
          </div>

          <div className="recognition-options">
            <div
              {...getRootProps()}
              className={`dropzone ${isDragActive ? 'active' : ''}`}
            >
              <input {...getInputProps()} />
              <Upload className="dropzone-icon" />
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
              <p>Analyzing audio... This may take a few moments.</p>
            </div>
          )}

          {error && (
            <div className="error-container">
              <p className="error-message">{error}</p>
            </div>
          )}

          {results && (
            <div className="results-container">
              <h3 className="results-title">
                <Search className="results-icon" />
                Recognition Results
              </h3>
              
              {results.success ? (
                <div className="results-list">
                    {results.matches.length > 0 ? (
                      results.matches.map((match, index) => (
                        <div key={index} className="result-item">
                          <div className="result-header">
                            <h4 className="result-title">{match.title}</h4>
                            <span className="result-confidence">
                              {Math.round(match.confidence * 100)}% match
                            </span>
                          </div>
                          <p className="result-artist">by {match.artist}</p>
                          <div className="result-details">
                            <span>Matches: {match.matches}</span>
                            <span>Time offset: {match.time_offset}s</span>
                            <button
                              className="btn btn-secondary visualization-btn"
                              onClick={() => handleViewVisualization(match)}
                              disabled={isLoading}
                            >
                              <Eye className="btn-icon" />
                              View Comparison
                            </button>
                          </div>
                        </div>
                      ))
                    ) : (
                    <div className="no-results">
                      <p>No matches found. Try a different audio clip.</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="no-results">
                  <p>{results.message}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {showVisualization && (
        <RecognitionVisualization
          isOpen={showVisualization}
          onClose={handleCloseVisualization}
          visualizationData={visualizationData}
          matchData={selectedMatch}
        />
      )}
    </div>
  );
};

export default Home;