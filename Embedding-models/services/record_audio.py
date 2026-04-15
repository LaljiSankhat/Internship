import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

# Configuration (embedding-friendly defaults)
SAMPLE_RATE = 16000   # Wav2Vec2 / Whisper standard
DURATION = 5          # seconds
CHANNELS = 1          # mono

def record_audio(filename="contents/recorded_audio.wav"):
    print("Recording audio for 5 seconds...")
    
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='float32'
    )
    
    sd.wait()
    print("Recording finished")

    # Convert float32 → int16 (required for wav)
    audio_int16 = np.int16(audio * 32767)

    write(filename, SAMPLE_RATE, audio_int16)
    print(f"Saved as {filename}")

record_audio()
