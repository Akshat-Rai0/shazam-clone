import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter
import hashlib
import librosa
from typing import List, Tuple, Dict
import os

# Fingerprinting parameters
SAMPLE_RATE = 22050
FFT_WINDOW_SIZE = 4096
OVERLAP_RATIO = 0.5
FAN_VALUE = 5
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 200
PEAK_NEIGHBORHOOD_SIZE = 10
MIN_AMPLITUDE = 10


def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
    """Load audio file"""
    try:
        print(f"   Loading: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        audio, sr = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)
        print(f"   ✅ Loaded {len(audio)} samples at {sr} Hz ({len(audio)/sr:.2f}s)")
        return audio, sr
    except Exception as e:
        print(f"   ❌ Load error: {str(e)}")
        raise


def generate_spectrogram(audio: np.ndarray) -> np.ndarray:
    """Generate spectrogram"""
    hop_length = int(FFT_WINDOW_SIZE * (1 - OVERLAP_RATIO))
    
    stft = librosa.stft(
        audio, 
        n_fft=FFT_WINDOW_SIZE, 
        hop_length=hop_length,
        window='hann'
    )
    
    spectrogram = np.abs(stft)
    print(f"   ✅ Spectrogram shape: {spectrogram.shape} (freq x time)")
    return spectrogram


def find_peaks(spectrogram: np.ndarray) -> List[Tuple[int, int]]:
    """Find peaks in spectrogram"""
    struct = np.ones((PEAK_NEIGHBORHOOD_SIZE, PEAK_NEIGHBORHOOD_SIZE))
    neighborhood = maximum_filter(spectrogram, footprint=struct)
    
    local_max = (spectrogram == neighborhood)
    background = (spectrogram < MIN_AMPLITUDE)
    eroded_background = maximum_filter(background, footprint=struct, mode='constant')
    
    detected_peaks = local_max & ~eroded_background
    peak_positions = np.where(detected_peaks)
    peaks = list(zip(peak_positions[1], peak_positions[0]))
    
    print(f"   ✅ Found {len(peaks)} peaks")
    return peaks


def generate_hashes(peaks: List[Tuple[int, int]]) -> List[Tuple[str, int]]:
    """Generate hashes from peaks"""
    peaks = sorted(peaks, key=lambda x: x[0])
    hashes = []
    
    for i in range(len(peaks)):
        for j in range(1, FAN_VALUE + 1):
            if i + j < len(peaks):
                freq1 = peaks[i][1]
                freq2 = peaks[i + j][1]
                time1 = peaks[i][0]
                time2 = peaks[i + j][0]
                
                time_delta = time2 - time1
                
                if MIN_HASH_TIME_DELTA <= time_delta <= MAX_HASH_TIME_DELTA:
                    hash_string = f"{freq1}|{freq2}|{time_delta}"
                    hash_value = hashlib.sha1(hash_string.encode()).hexdigest()
                    hashes.append((hash_value, time1))
    
    print(f"   ✅ Generated {len(hashes)} hashes")
    return hashes


def fingerprint_audio(file_path: str) -> List[Tuple[str, float]]:
    """Generate fingerprints for audio file"""
    print(f"\n🎵 Fingerprinting: {os.path.basename(file_path)}")
    
    # Load
    audio, sr = load_audio(file_path)
    
    # Spectrogram
    print(f"�� Generating spectrogram...")
    spectrogram = generate_spectrogram(audio)
    
    # Peaks
    print(f"🔍 Finding peaks...")
    peaks = find_peaks(spectrogram)
    
    if len(peaks) == 0:
        print(f"⚠️  No peaks found!")
        return []
    
    # Hashes
    print(f"🔐 Generating hashes...")
    hashes = generate_hashes(peaks)
    
    if len(hashes) == 0:
        print(f"⚠️  No hashes generated!")
        return []
    
    # Convert to seconds
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
    """Match fingerprints against database"""
    matches = {}
    
    for query_hash, query_time in query_hashes:
        if query_hash in db_fingerprints:
            for song_id, db_time in db_fingerprints[query_hash]:
                if song_id not in matches:
                    matches[song_id] = {'count': 0, 'time_diffs': []}
                
                time_diff = db_time - query_time
                matches[song_id]['time_diffs'].append(time_diff)
                matches[song_id]['count'] += 1
    
    results = {}
    for song_id, data in matches.items():
        match_count = data['count']
        time_diffs = data['time_diffs']
        
        if len(time_diffs) > 0:
            time_consistency = np.std(time_diffs)
        else:
            time_consistency = float('inf')
        
        confidence = match_count / (1 + time_consistency)
        
        results[song_id] = {
            'matches': match_count,
            'confidence': round(confidence, 2),
            'avg_time_offset': round(np.mean(time_diffs), 2) if time_diffs else 0
        }
    
    return results
