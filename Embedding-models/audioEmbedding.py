import wave
import torch
import soundfile as sf
from transformers import Wav2Vec2Processor, Wav2Vec2Model
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import torchaudio
import librosa
import noisereduce as nr

# Load model once
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
model.eval()

def audio_to_embedding(audio_path: str) -> torch.Tensor:
    waveform, sample_rate = sf.read(audio_path)

    # Convert to mono
    if waveform.ndim > 1:
        waveform = waveform.mean(axis=1)

    # Resample to 16kHz if needed
    waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=16000)
    sr = 16000

    waveform = nr.reduce_noise(y=waveform, sr=sr)

    # Z-score normalization std = 1, mean 0
    mean = waveform.mean()
    std = waveform.std()
    mini = waveform.min()
    maxi = waveform.max()

    # waveform = waveform - mini / (maxi - mini)
    if std > 0:
        waveform = (waveform - mean) / std
    else:
        waveform = waveform - mean 

    inputs = processor(
        waveform,
        sampling_rate=16000,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**inputs)
    
    # print("This is output from the model \n", outputs)

    # Mean pooling → single vector
    embedding = outputs.last_hidden_state.mean(dim=1)

    print("\n output of embeddings \n ", embedding.shape)

    return embedding.squeeze(0)  # shape: [768]


audio_files = [
    "contents/me.wav",
    "contents/m.wav",
    "contents/Lalji3.wav",
]

embeddings = []
for path in audio_files:
    emb = audio_to_embedding(path)
    embeddings.append(emb)

embeddings = torch.stack(embeddings)  # shape: [N, 768]


print(euclidean_distances([embeddings[0]], [embeddings[1]]))
print(euclidean_distances([embeddings[0]], [embeddings[2]]))
print(euclidean_distances([embeddings[2]], [embeddings[1]]))

print(cosine_similarity(embeddings))
