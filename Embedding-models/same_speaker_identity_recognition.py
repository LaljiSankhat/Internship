import torch
import soundfile as sf
import librosa
from transformers import AutoProcessor, AutoModel
import noisereduce as nr          
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances


MODEL_NAME = "facebook/wav2vec2-base"
processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)


def load_audio(path):
    # Load audio
    waveform, sr = sf.read(path)

    # Downmix to mono
    if waveform.ndim > 1:
        waveform = waveform.mean(axis=1)
    
    # Resample to 16k (waveform2vec requirement)
    waveform = librosa.resample(waveform, orig_sr=sr, target_sr=16000)
    sr = 16000

    # noise reduction
    waveform = nr.reduce_noise(y=waveform, sr=sr)

    # Z-score normalization std = 1, mean 0
    mean = waveform.mean()
    std = waveform.std()
    if std > 0:
        waveform = (waveform - mean) / std
    else:
        waveform = waveform - mean   # silent audio fallback
    return torch.tensor(waveform, dtype=torch.float32), sr


def embed_audio(path):
    waveform, sr = load_audio(path)
    inputs = processor(waveform, sampling_rate=sr, return_tensors="pt", padding=True)
    with torch.no_grad():
        out = model(**inputs).last_hidden_state
        embedding = out.mean(dim=1)
    return embedding.squeeze()  


audio_files = {
    "contents/m.wav",
    "contents/Lalji.wav",
    "contents/Lalji3.wav",
}

embeddings_list = []
for path in audio_files:
    emb = embed_audio(path)
    embeddings_list.append(emb)


embeddings_tensor = torch.stack(embeddings_list)
sim_matrix = cosine_similarity(embeddings_tensor.numpy())

a_vs_b = euclidean_distances([embeddings_tensor[0]], [embeddings_tensor[1]])
a_vs_c = euclidean_distances([embeddings_tensor[0]], [embeddings_tensor[2]])
b_vs_c = euclidean_distances([embeddings_tensor[2]], [embeddings_tensor[1]])

print("euclidean distances for person A and person B",a_vs_b)
print("euclidean distances for person A and person C",a_vs_c)
print("euclidean distances for person C and person B",b_vs_c)


print("Cosine simi \n ", sim_matrix)