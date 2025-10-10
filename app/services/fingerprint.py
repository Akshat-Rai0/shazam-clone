"""
Audio Fingerprinting Service

This module implements the core audio fingerprinting algorithm inspired by Shazam.
The algorithm works by:
1. Converting audio to a spectrogram (frequency vs time representation)
2. Finding peaks (local maxima) in the spectrogram
3. Creating combinatorial hashes from peak pairs
4. Storing hashes with time offsets for later matching

Reference: "An Industrial-Strength Audio Search Algorithm" by Avery Wang (2003)
"""

import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter
import hashlib
import librosa
from typing import List, Tuple, Dict
import os

# ============================================================================
# FINGERPRINTING PARAMETERS
# ============================================================================
# These parameters control the fingerprinting algorithm's behavior
# Tuning these affects both accuracy and performance

SAMPLE_RATE = 22050              # Audio sample rate (Hz) - standard for music analysis
FFT_WINDOW_SIZE = 4096           # Spectrogram window size - larger = better freq resolution
OVERLAP_RATIO = 0.5              # Window overlap - higher = more time resolution
FAN_VALUE = 5                    # Number of peaks to pair with each anchor - higher = more hashes
MIN_HASH_TIME_DELTA = 0          # Minimum time between paired peaks (frames)
MAX_HASH_TIME_DELTA = 200        # Maximum time between paired peaks (frames)
PEAK_NEIGHBORHOOD_SIZE = 10      # Size of region to check for local maxima
MIN_AMPLITUDE = 1              # Minimum amplitude for a peak to be considered


def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
    """
    Load and preprocess audio file.
    
    Converts audio to:
    - Mono channel (single channel)
    - Standard sample rate (22050 Hz)
    - Normalized amplitude
    
    Args:
        file_path: Path to audio file (supports MP3, WAV, FLAC, etc.)
    
    Returns:
        Tuple of (audio_data, sample_rate)
        - audio_data: 1D numpy array of audio samples
        - sample_rate: Sample rate in Hz
    
    Raises:
        FileNotFoundError: If audio file doesn't exist
        Exception: If audio file is corrupted or unsupported format
    """
    try:
        print(f"   Loading: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # librosa.load automatically converts to mono and resamples
        audio, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
        print(f"   ✅ Loaded {len(audio)} samples at {sr} Hz ({len(audio)/sr:.2f}s)")
        return audio, sr
    except Exception as e:
        print(f"   ❌ Load error: {str(e)}")
        raise


def generate_spectrogram(audio: np.ndarray) -> np.ndarray:
    """
    Generate spectrogram from audio using Short-Time Fourier Transform (STFT).
    
    A spectrogram is a visual representation showing how the frequency content
    of a signal varies over time. It's like sheet music for digital audio.
    
    The STFT works by:
    1. Dividing audio into overlapping windows
    2. Applying FFT to each window
    3. Stacking results to create a 2D time-frequency representation
    
    Args:
        audio: 1D array of audio samples
    
    Returns:
        2D numpy array of shape (frequency_bins, time_frames)
        Values represent magnitude at each frequency and time
    """
    # Calculate hop length (samples to advance between windows)
    hop_length = int(FFT_WINDOW_SIZE * (1 - OVERLAP_RATIO))
    
    # Perform Short-Time Fourier Transform
    # - n_fft: FFT window size (frequency resolution)
    # - hop_length: overlap between windows (time resolution)
    # - window: Hann window reduces spectral leakage
    stft = librosa.stft(
        audio, 
        n_fft=FFT_WINDOW_SIZE, 
        hop_length=hop_length,
        window='hann'
    )
    
    # Convert complex STFT to magnitude spectrogram
    spectrogram = np.abs(stft)
    print(f"   ✅ Spectrogram shape: {spectrogram.shape} (freq x time)")
    return spectrogram


def find_peaks(spectrogram: np.ndarray) -> List[Tuple[int, int]]:
    """
    Find local maxima (peaks) in the spectrogram.
    
    Peaks represent the most prominent frequencies at each time point.
    These are the "constellation points" that make up the audio fingerprint.
    
    Algorithm:
    1. Apply maximum filter to find neighborhood maxima
    2. Keep only points that are local maxima AND above threshold
    3. Remove background noise using erosion
    
    Args:
        spectrogram: 2D array from generate_spectrogram()
    
    Returns:
        List of (time_index, frequency_index) tuples representing peak locations
        
    Example:
        peaks = [(0, 100), (5, 150), ...]
        means: peak at time=0, freq=100; peak at time=5, freq=150
    """
    # Create structuring element for neighborhood comparison
    # This defines what "local" means - a square region of PEAK_NEIGHBORHOOD_SIZE
    struct = np.ones((PEAK_NEIGHBORHOOD_SIZE, PEAK_NEIGHBORHOOD_SIZE))
    
    # Find maximum value in each neighborhood
    neighborhood = maximum_filter(spectrogram, footprint=struct)
    
    # A peak is where the value equals the neighborhood maximum
    local_max = (spectrogram == neighborhood)
    
    # Remove peaks that are below our amplitude threshold (likely noise)
    background = (spectrogram < MIN_AMPLITUDE)
    eroded_background = maximum_filter(background, footprint=struct, mode='constant')
    
    # Final peaks: local maxima that aren't in the background
    detected_peaks = local_max & ~eroded_background
    
    # Convert boolean mask to list of (time, frequency) coordinates
    peak_positions = np.where(detected_peaks)
    peaks = list(zip(peak_positions[1], peak_positions[0]))  # (time, freq) format
    
    print(f"   ✅ Found {len(peaks)} peaks")
    return peaks


def generate_hashes(peaks: List[Tuple[int, int]]) -> List[Tuple[str, int]]:
    """
    Generate combinatorial hashes from peak pairs.
    
    This is the core of the fingerprinting algorithm. Each peak becomes an "anchor"
    that's paired with nearby peaks in the future to create unique hashes.
    
    Why combinatorial hashes?
    - Robust to noise (some peaks may be missed, but others survive)
    - Time-invariant (same pattern = same hash, regardless of when it occurs)
    - Unique enough to distinguish songs
    
    Hash format: SHA1(freq1|freq2|time_delta)
    - freq1: frequency of anchor peak
    - freq2: frequency of target peak
    - time_delta: time difference between peaks
    
    Args:
        peaks: List of (time, frequency) peak coordinates
    
    Returns:
        List of (hash_string, anchor_time) tuples
        - hash_string: 40-character SHA1 hex string
        - anchor_time: time index of the anchor peak (for offset calculation)
    
    Example:
        If anchor peak at (t=10, f=100) pairs with target at (t=15, f=200):
        Hash = SHA1("100|200|5") = "a3f2e..."
        Stored as ("a3f2e...", 10)
    """
    # Sort peaks by time to ensure we pair in chronological order
    peaks = sorted(peaks, key=lambda x: x[0])
    hashes = []
    
    # For each peak, create hashes by pairing with future peaks
    for i in range(len(peaks)):
        # Try to pair with next FAN_VALUE peaks
        for j in range(1, FAN_VALUE + 1):
            if i + j < len(peaks):
                # Extract coordinates
                freq1 = peaks[i][1]      # Anchor frequency
                freq2 = peaks[i + j][1]  # Target frequency
                time1 = peaks[i][0]      # Anchor time
                time2 = peaks[i + j][0]  # Target time
                
                time_delta = time2 - time1
                
                # Only create hash if time difference is within valid range
                # This prevents pairing peaks that are too close or too far apart
                if MIN_HASH_TIME_DELTA <= time_delta <= MAX_HASH_TIME_DELTA:
                    # Create hash string from frequency pair and time delta
                    hash_string = f"{freq1}|{freq2}|{time_delta}"
                    
                    # Convert to SHA1 hash for consistent length and distribution
                    hash_value = hashlib.sha1(hash_string.encode()).hexdigest()
                    
                    # Store hash with anchor time for offset calculation during matching
                    hashes.append((hash_value, time1))
    
    print(f"   ✅ Generated {len(hashes)} hashes")
    return hashes


def fingerprint_audio(file_path: str) -> List[Tuple[str, float]]:
    """
    Complete fingerprinting pipeline for an audio file.
    
    This is the main entry point for fingerprinting. It orchestrates all steps:
    1. Load audio file
    2. Generate spectrogram
    3. Find peaks
    4. Generate hashes
    5. Convert to real time units (seconds)
    
    Args:
        file_path: Path to audio file
    
    Returns:
        List of (hash_value, time_offset) tuples
        - hash_value: 40-char SHA1 hash string
        - time_offset: Time in SECONDS where this hash occurs
    
    The returned fingerprints are ready to be stored in the database.
    """
    print(f"\n🎵 Fingerprinting: {os.path.basename(file_path)}")
    
    # Step 1: Load audio
    audio, sr = load_audio(file_path)
    
    # Step 2: Generate spectrogram
    print(f"📊 Generating spectrogram...")
    spectrogram = generate_spectrogram(audio)
    
    # Step 3: Find peaks
    print(f"🔍 Finding peaks...")
    peaks = find_peaks(spectrogram)
    
    if len(peaks) == 0:
        print(f"⚠️  No peaks found!")
        return []
    
    # Step 4: Generate hashes
    print(f"🔐 Generating hashes...")
    hashes = generate_hashes(peaks)
    
    if len(hashes) == 0:
        print(f"⚠️  No hashes generated!")
        return []
    
    # Step 5: Convert time indices to seconds
    # Each time index represents one hop_length of samples
    hop_length = int(FFT_WINDOW_SIZE * (1 - OVERLAP_RATIO))
    time_to_seconds = hop_length / SAMPLE_RATE
    
    fingerprints = [
        (hash_val, time_idx * time_to_seconds) 
        for hash_val, time_idx in hashes
    ]
    
    print(f"✅ Complete: {len(fingerprints)} fingerprints\n")
    return fingerprints


def match_fingerprints(
    query_hashes: List[Tuple[str, float]], 
    db_fingerprints: Dict[str, List[Tuple[int, float]]]
) -> Dict[int, Dict]:
    """
    Match query fingerprints against database fingerprints.
    
    Matching algorithm:
    1. For each query hash, look up matching database hashes
    2. Calculate time offset difference for each match
    3. Group matches by song_id
    4. Score based on:
       - Number of matching hashes (more = better)
       - Time consistency (smaller std dev = better alignment)
    
    Why time consistency matters:
    If a query matches a song, the time offsets should be consistent.
    For example, if the query starts at 30s in the song, ALL matched
    hashes should indicate ~30s offset. Inconsistent offsets suggest
    random/false matches.
    
    Args:
        query_hashes: List of (hash, time) from query audio
        db_fingerprints: Dict mapping hash -> [(song_id, time), ...]
    
    Returns:
        Dict mapping song_id -> match statistics:
        {
            song_id: {
                'matches': int,           # Number of matching hashes
                'confidence': float,      # Confidence score
                'avg_time_offset': float  # Where in song the query appears
            }
        }
    
    Example:
        If 100 query hashes match song_id=5, all with ~30s offset:
        {
            5: {
                'matches': 100,
                'confidence': 85.2,
                'avg_time_offset': 30.1
            }
        }
    """
    matches = {}
    
    # Step 1: Find all hash matches
    for query_hash, query_time in query_hashes:
        if query_hash in db_fingerprints:
            # This hash exists in database - check which songs have it
            for song_id, db_time in db_fingerprints[query_hash]:
                if song_id not in matches:
                    matches[song_id] = {'count': 0, 'time_diffs': []}
                
                # Calculate time offset: where in the song does this match occur?
                # If db_time=30s and query_time=0s, query starts at 30s in song
                time_diff = db_time - query_time
                matches[song_id]['time_diffs'].append(time_diff)
                matches[song_id]['count'] += 1
    
    # Step 2: Calculate confidence scores
    results = {}
    for song_id, data in matches.items():
        match_count = data['count']
        time_diffs = data['time_diffs']
        
        # Calculate time consistency (standard deviation)
        # Lower std dev = more consistent = better match
        if len(time_diffs) > 0:
            time_consistency = np.std(time_diffs)
        else:
            time_consistency = float('inf')
        
        # Confidence score: matches divided by (1 + inconsistency)
        # More matches = higher score
        # Lower inconsistency = higher score
        confidence = match_count / (1 + time_consistency)
        
        results[song_id] = {
            'matches': match_count,
            'confidence': round(confidence, 2),
            'avg_time_offset': round(np.mean(time_diffs), 2) if time_diffs else 0
        }
    
    return results