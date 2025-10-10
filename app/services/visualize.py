import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import numpy as np
import librosa
import librosa.display
from pathlib import Path
import io
import base64
from typing import Optional

def generate_spectrogram_image(
    file_path: str, 
    output_path: Optional[str] = None,
    return_base64: bool = True
) -> Optional[str]:
    """
    Generate spectrogram visualization from audio file
    
    Args:
        file_path: Path to audio file
        output_path: Optional path to save image
        return_base64: If True, return base64 encoded image string
    
    Returns:
        Base64 encoded image string if return_base64=True, else None
    """
    try:
        # Load audio
        y, sr = librosa.load(file_path, sr=22050)
        
        # Create figure
        plt.figure(figsize=(12, 6))
        
        # Generate mel spectrogram
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        # Plot
        img = librosa.display.specshow(
            S_dB, 
            sr=sr, 
            x_axis='time', 
            y_axis='mel',
            cmap='viridis'
        )
        
        plt.colorbar(img, format='%+2.0f dB')
        plt.title('Mel-frequency spectrogram', fontsize=14)
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.tight_layout()
        
        # Save or return base64
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        elif return_base64:
            # Convert to base64 for API response
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"
        else:
            plt.close()
            return None
            
    except Exception as e:
        plt.close()
        raise Exception(f"Error generating spectrogram: {str(e)}")


def generate_peaks_visualization(
    file_path: str,
    peaks: list,
    return_base64: bool = True
) -> Optional[str]:
    """
    Generate spectrogram with detected peaks overlaid
    
    Args:
        file_path: Path to audio file
        peaks: List of (time, frequency) peak coordinates
        return_base64: If True, return base64 encoded image
    
    Returns:
        Base64 encoded image string if return_base64=True
    """
    try:
        # Load audio
        y, sr = librosa.load(file_path, sr=22050)
        
        # Create spectrogram
        D = librosa.stft(y, n_fft=4096, hop_length=2048)
        S_dB = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        
        # Create figure
        plt.figure(figsize=(14, 8))
        
        # Plot spectrogram
        img = librosa.display.specshow(
            S_dB,
            sr=sr,
            hop_length=2048,
            x_axis='time',
            y_axis='hz',
            cmap='inferno'
        )
        
        # Overlay peaks
        if peaks and len(peaks) > 0:
            # Convert peak indices to actual time/frequency
            times = [p[0] * 2048 / sr for p in peaks[:1000]]  # Limit to 1000 peaks for visibility
            freqs = [p[1] * sr / 4096 for p in peaks[:1000]]
            
            plt.scatter(
                times, 
                freqs, 
                c='red', 
                s=10, 
                alpha=0.6, 
                marker='x',
                label=f'Peaks (showing {min(len(peaks), 1000)} of {len(peaks)})'
            )
            plt.legend(loc='upper right')
        
        plt.colorbar(img, format='%+2.0f dB')
        plt.title('Spectrogram with Detected Peaks', fontsize=14, fontweight='bold')
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.tight_layout()
        
        if return_base64:
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"
        else:
            plt.close()
            return None
            
    except Exception as e:
        plt.close()
        raise Exception(f"Error generating peaks visualization: {str(e)}")


def generate_comparison_visualization(
    query_path: str,
    matched_path: str,
    return_base64: bool = True
) -> Optional[str]:
    """
    Generate side-by-side comparison of query and matched song spectrograms
    """
    try:
        # Load both audio files
        y1, sr1 = librosa.load(query_path, sr=22050, duration=30)
        y2, sr2 = librosa.load(matched_path, sr=22050, duration=30)
        
        # Create spectrograms
        S1 = librosa.feature.melspectrogram(y=y1, sr=sr1)
        S1_dB = librosa.power_to_db(S1, ref=np.max)
        
        S2 = librosa.feature.melspectrogram(y=y2, sr=sr2)
        S2_dB = librosa.power_to_db(S2, ref=np.max)
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Query spectrogram
        img1 = librosa.display.specshow(
            S1_dB, sr=sr1, x_axis='time', y_axis='mel',
            cmap='viridis', ax=ax1
        )
        ax1.set_title('Query Audio', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Frequency (Hz)')
        fig.colorbar(img1, ax=ax1, format='%+2.0f dB')
        
        # Matched spectrogram
        img2 = librosa.display.specshow(
            S2_dB, sr=sr2, x_axis='time', y_axis='mel',
            cmap='viridis', ax=ax2
        )
        ax2.set_title('Matched Song', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Frequency (Hz)')
        fig.colorbar(img2, ax=ax2, format='%+2.0f dB')
        
        plt.tight_layout()
        
        if return_base64:
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"
        else:
            plt.close()
            return None
            
    except Exception as e:
        plt.close()
        raise Exception(f"Error generating comparison: {str(e)}")
