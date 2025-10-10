import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Mic, Upload, Music, Search } from 'lucide-react';
import { recognizeAudio } from '../services/api';
import './Home.css';

const Home = ({ isLoading, setIsLoading }) => {
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await recognizeAudio(file);
      setResults(response);
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

  const startRecording = () => {
    setIsRecording(true);
    // TODO: Implement actual recording functionality
    setTimeout(() => {
      setIsRecording(false);
      setError('Recording functionality not implemented yet. Please upload an audio file.');
    }, 3000);
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

            <div className="divider">
              <span>or</span>
            </div>

            <button
              className={`btn btn-secondary ${isRecording ? 'recording' : ''}`}
              onClick={startRecording}
              disabled={isLoading}
            >
              <Mic className="btn-icon" />
              {isRecording ? 'Recording...' : 'Record Audio'}
            </button>
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
    </div>
  );
};

export default Home;