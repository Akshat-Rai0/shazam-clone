import React from 'react';
import { Upload as UploadIcon, Music, Info } from 'lucide-react';
import './Upload.css';

const Upload = () => {
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
            <h2 className="card-title">Upload Disabled</h2>
            <p className="card-subtitle">
              Song upload functionality is not available in this demo
            </p>
          </div>

          <div className="upload-disabled-notice">
            <div className="notice-icon">
              <Info size={48} />
            </div>
            <div className="notice-content">
              <h3>Upload Feature Disabled</h3>
              <p>
                Song upload is disabled in this demo deployment. 
                The system comes pre-loaded with 5 test songs for audio recognition testing.
              </p>
              <p>
                To test the recognition feature, please:
              </p>
              <ul>
                <li>Visit the <strong>Library</strong> page to see the pre-loaded songs</li>
                <li>Go to the <strong>Home</strong> page to upload audio clips for recognition</li>
                <li>Record or upload a short audio clip from one of the pre-loaded songs</li>
              </ul>
              <p className="notice-note">
                <Music size={16} />
                The pre-loaded songs include various genres and styles to demonstrate the recognition system.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;