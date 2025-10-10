import React, { useState, useEffect } from 'react';
import { BarChart3, Music, Database, TrendingUp, Clock } from 'lucide-react';
import { getRecognitionStats } from '../services/api';
import './Stats.css';

const Stats = ({ isLoading, setIsLoading }) => {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const statsData = await getRecognitionStats();
      setStats(statsData);
    } catch (err) {
      setError(err.message || 'Failed to load statistics');
    }
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return '#4CAF50';
    if (percentage >= 60) return '#FF9800';
    return '#f44336';
  };

  return (
    <div className="stats">
      <div className="stats-header">
        <h1 className="stats-title">
          <BarChart3 className="stats-icon" />
          Recognition Statistics
        </h1>
        <p className="stats-subtitle">
          Monitor your audio recognition system performance
        </p>
      </div>

      <div className="stats-content">
        {error && (
          <div className="error-container">
            <p className="error-message">{error}</p>
          </div>
        )}

        {stats && (
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <Music className="icon" />
              </div>
              <div className="stat-content">
                <div className="stat-number">{stats.total_songs}</div>
                <div className="stat-label">Total Songs</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <Database className="icon" />
              </div>
              <div className="stat-content">
                <div className="stat-number">{stats.processed_songs}</div>
                <div className="stat-label">Processed Songs</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <Clock className="icon" />
              </div>
              <div className="stat-content">
                <div className="stat-number">{stats.pending_songs}</div>
                <div className="stat-label">Pending Songs</div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <TrendingUp className="icon" />
              </div>
              <div className="stat-content">
                <div className="stat-number">{stats.total_fingerprints.toLocaleString()}</div>
                <div className="stat-label">Total Fingerprints</div>
              </div>
            </div>

            <div className="stat-card large">
              <div className="stat-header">
                <h3 className="stat-title">Processing Progress</h3>
                <div className="stat-percentage">
                  {stats.processed_songs > 0 
                    ? Math.round((stats.processed_songs / stats.total_songs) * 100)
                    : 0}%
                </div>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{
                    width: `${stats.processed_songs > 0 
                      ? (stats.processed_songs / stats.total_songs) * 100 
                      : 0}%`,
                    backgroundColor: getProgressColor(
                      stats.processed_songs > 0 
                        ? (stats.processed_songs / stats.total_songs) * 100 
                        : 0
                    )
                  }}
                ></div>
              </div>
              <div className="progress-text">
                {stats.processed_songs} of {stats.total_songs} songs processed
              </div>
            </div>

            <div className="stat-card large">
              <div className="stat-header">
                <h3 className="stat-title">Fingerprint Density</h3>
                <div className="stat-number">{stats.avg_fingerprints_per_song}</div>
              </div>
              <div className="fingerprint-info">
                <p>Average fingerprints per song</p>
                <div className="fingerprint-bar">
                  <div 
                    className="fingerprint-fill"
                    style={{
                      width: `${Math.min((stats.avg_fingerprints_per_song / 1000) * 100, 100)}%`
                    }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="stat-card status">
              <div className="status-header">
                <h3 className="stat-title">System Status</h3>
                <div className={`status-indicator ${stats.ready_for_recognition ? 'ready' : 'not-ready'}`}>
                  {stats.ready_for_recognition ? '✓' : '⚠'}
                </div>
              </div>
              <div className="status-message">
                {stats.ready_for_recognition 
                  ? 'System is ready for audio recognition'
                  : 'System needs more processed songs for recognition'
                }
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Stats;