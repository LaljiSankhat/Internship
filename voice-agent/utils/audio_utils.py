"""Audio utility functions"""
import numpy as np
import soundfile as sf
import librosa


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int = 24000) -> np.ndarray:
    """Resample audio to target sample rate"""
    return librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalize audio to [-1, 1] range"""
    max_val = np.abs(audio).max()
    if max_val > 0:
        return audio / max_val
    return audio


def load_audio_file(file_path: str, target_sr: int = 24000) -> tuple[np.ndarray, int]:
    """Load audio file and resample if needed"""
    audio, sr = sf.read(file_path)
    if sr != target_sr:
        audio = resample_audio(audio, sr, target_sr)
    return normalize_audio(audio), target_sr
