import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 30 seconds timeout for file uploads
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Audio Recognition
export const recognizeAudio = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post('/recognize/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Recognition failed');
  }
};

export const recognizeWithVisualization = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post('/recognize/with-visualization', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Recognition with visualization failed');
  }
};

// Artists
export const getArtists = async () => {
  try {
    const response = await api.get('/artists/');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch artists');
  }
};

export const createArtist = async (name) => {
  try {
    const response = await api.post('/artists/', { name });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to create artist');
  }
};

export const getArtist = async (id) => {
  try {
    const response = await api.get(`/artists/${id}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch artist');
  }
};

export const updateArtist = async (id, data) => {
  try {
    const response = await api.put(`/artists/${id}`, data);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to update artist');
  }
};

export const deleteArtist = async (id) => {
  try {
    const response = await api.delete(`/artists/${id}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to delete artist');
  }
};

// Songs
export const getSongs = async () => {
  try {
    const response = await api.get('/songs/');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch songs');
  }
};

export const getSong = async (id) => {
  try {
    const response = await api.get(`/songs/${id}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch song');
  }
};

export const deleteSong = async (id) => {
  try {
    const response = await api.delete(`/songs/${id}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to delete song');
  }
};

// Upload
export const uploadSong = async (file, title, artistId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);
  formData.append('artist_id', artistId);
  
  try {
    const response = await api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Upload failed');
  }
};

export const getUploadInfo = async (songId) => {
  try {
    const response = await api.get(`/upload/info/${songId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch upload info');
  }
};

export const getUploadStatus = async () => {
  try {
    const response = await api.get('/upload/status');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch upload status');
  }
};

export const deleteUpload = async (songId) => {
  try {
    const response = await api.delete(`/upload/${songId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to delete upload');
  }
};

// Recognition Stats
export const getRecognitionStats = async () => {
  try {
    const response = await api.get('/recognize/stats');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch recognition stats');
  }
};

// Visualizations
export const getAllVisualizations = async () => {
  try {
    const response = await api.get('/visualize/all');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch visualizations');
  }
};

export const getSongVisualization = async (songId, showPeaks = false) => {
  try {
    const response = await api.get(`/visualize/api/spectrogram/${songId}?show_peaks=${showPeaks}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch song visualization');
  }
};

// Health Check
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Health check failed');
  }
};

export default api;