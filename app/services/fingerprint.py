import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter
import hashlib
import librosa
from typing import List, Tuple, Dict
import os

# Fingerprinting parameters
SAMPLE_RATE = 22050  # Hz
FFT_WINDOW_SIZE = 4096  # samples
OVERLAP_RATIO = 0.5
FAN_VALUE = 5  # Number of peaks to pair with each peak
MIN_HASH_TIME_DELTA = 0  # seconds
MAX_HASH_TIME_DELTA = 200  # seconds
PEAK_NEIGHBORHOOD_SIZE = 10
MIN_AMPLITUDE = 10


def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
    """
    Load audio file and convert to mono
    Returns: (audio_data, sample_rate)
    """
    try:
        # Load audio file
        audio, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
        return audio, sr
    except Exception as e:
        raise Exception(f"Error loading audio file: {str(e)}")


def generate_spectrogram(audio: np.ndarray) -> np.ndarray:
    """
    Generate spectrogram from audio data using STFT
    Returns: 2D array (frequency x time)
    """
    # Short-Time Fourier Transform
    hop_length = int(FFT_WINDOW_SIZE * (1 - OVERLAP_RATIO))
    
    # Compute spectrogram
    stft = librosa.stft(
        audio, 
        n_fft=FFT_WINDOW_SIZE, 
        hop_length=hop_length,
        window='hann'
    )
    
    # Convert to magnitude spectrogram
    spectrogram = np.abs(stft)
    
    return spectrogram


def find_peaks(spectrogram: np.ndarray) -> List[Tuple[int, int]]:
    """
    Find local peaks in the spectrogram
    Returns: List of (time_index, frequency_index) tuples
    """
    # Apply maximum filter to find local maxima
    struct = np.ones((PEAK_NEIGHBORHOOD_SIZE, PEAK_NEIGHBORHOOD_SIZE))
    neighborhood = maximum_filter(spectrogram, footprint=struct)
    
    # Find where spectrogram equals the local maximum
    local_max = (spectrogram == neighborhood)
    
    # Remove peaks below amplitude threshold
    background = (spectrogram < MIN_AMPLITUDE)
    eroded_background = maximum_filter(background, footprint=struct, mode='constant')
    
    # Boolean mask of peaks (local maxima above threshold)
    detected_peaks = local_max & ~eroded_background
    
    # Get coordinates of peaks
    peak_positions = np.where(detected_peaks)
    peaks = list(zip(peak_positions[1], peak_positions[0]))  # (time, freq)
    
    return peaks


def generate_hashes(peaks: List[Tuple[int, int]]) -> List[Tuple[str, int]]:
    """
    Generate hashes from peak pairs
    Returns: List of (hash_string, time_offset) tuples
    """
    # Sort peaks by time
    peaks = sorted(peaks, key=lambda x: x[0])
    
    hashes = []
    
    # For each peak, pair it with FAN_VALUE subsequent peaks
    for i in range(len(peaks)):
        for j in range(1, FAN_VALUE + 1):
            if i + j < len(peaks):
                freq1 = peaks[i][1]
                freq2 = peaks[i + j][1]
                time1 = peaks[i][0]
                time2 = peaks[i + j][0]
                
                time_delta = time2 - time1
                
                # Only consider pairs within time window
                if MIN_HASH_TIME_DELTA <= time_delta <= MAX_HASH_TIME_DELTA:
                    # Create hash from frequency pair and time delta
                    hash_string = f"{freq1}|{freq2}|{time_delta}"
                    
                    # Use SHA1 for consistent hash length
                    hash_value = hashlib.sha1(hash_string.encode()).hexdigest()
                    
                    # Store hash with its time offset
                    hashes.append((hash_value, time1))
    
    return hashes


def fingerprint_audio(file_path: str) -> List[Tuple[str, float]]:
    """
    Generate fingerprints for an audio file
    Returns: List of (hash, time_offset_seconds) tuples
    """
    print(f"📊 Loading audio: {file_path}")
    audio, sr = load_audio(file_path)
    
    print(f"📈 Generating spectrogram...")
    spectrogram = generate_spectrogram(audio)
    
    print(f"🔍 Finding peaks...")
    peaks = find_peaks(spectrogram)
    print(f"   Found {len(peaks)} peaks")
    
    print(f"🔐 Generating hashes...")
    hashes = generate_hashes(peaks)
    print(f"   Generated {len(hashes)} hashes")
    
    # Convert time indices to seconds
    hop_length = int(FFT_WINDOW_SIZE * (1 - OVERLAP_RATIO))
    time_to_seconds = hop_length / SAMPLE_RATE
    
    fingerprints = [
        (hash_val, time_idx * time_to_seconds) 
        for hash_val, time_idx in hashes
    ]
    
    return fingerprints


def match_fingerprints(
    query_hashes: List[Tuple[str, float]], 
    db_fingerprints: Dict[str, List[Tuple[int, float]]]
) -> Dict[int, Dict]:
    """
    Match query fingerprints against database
    
    Args:
        query_hashes: List of (hash, time_offset) from query audio
        db_fingerprints: Dict of {hash: [(song_id, time_offset), ...]}
    
    Returns:
        Dict of {song_id: {'matches': count, 'confidence': score}}
    """
    matches = {}
    
    for query_hash, query_time in query_hashes:
        if query_hash in db_fingerprints:
            for song_id, db_time in db_fingerprints[query_hash]:
                if song_id not in matches:
                    matches[song_id] = {'count': 0, 'time_diffs': []}
                
                # Time difference between query and database
                time_diff = db_time - query_time
                matches[song_id]['time_diffs'].append(time_diff)
                matches[song_id]['count'] += 1
    
    # Calculate confidence scores
    results = {}
    for song_id, data in matches.items():
        # More matches = higher confidence
        match_count = data['count']
        
        # Consistent time differences = higher confidence (song alignment)
        time_diffs = data['time_diffs']
        if len(time_diffs) > 0:
            # Standard deviation of time diffs (lower = more consistent)
            time_consistency = np.std(time_diffs)
        else:
            time_consistency = float('inf')
        
        # Simple confidence score (can be improved)
        confidence = match_count / (1 + time_consistency)
        
        results[song_id] = {
            'matches': match_count,
            'confidence': round(confidence, 2),
            'avg_time_offset': round(np.mean(time_diffs), 2) if time_diffs else 0
        }
    
    return results


def recognize_audio(file_path: str, db_fingerprints: Dict[str, List[Tuple[int, float]]]) -> List[Dict]:
    """
    Recognize audio file by matching against database
    
    Returns: List of matches sorted by confidence
    """
    # Generate fingerprints for query audio
    query_fingerprints = fingerprint_audio(file_path)
    
    # Match against database
    matches = match_fingerprints(query_fingerprints, db_fingerprints)
    
    # Sort by confidence
    sorted_matches = sorted(
        matches.items(), 
        key=lambda x: x[1]['confidence'], 
        reverse=True
    )
    
    return [
        {'song_id': song_id, **match_data} 
        for song_id, match_data in sorted_matches
    ]
