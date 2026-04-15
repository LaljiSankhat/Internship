import torch
import soundfile as sf
import noisereduce as nr
import librosa


import torchaudio
if not hasattr(torchaudio, "list_audio_backends"):
    torchaudio.list_audio_backends = lambda: []
if not hasattr(torchaudio, "get_audio_backend"):
    torchaudio.get_audio_backend = lambda: "soundfile"
if not hasattr(torchaudio, "set_audio_backend"):
    torchaudio.set_audio_backend = lambda x: None


from speechbrain.inference.speaker import EncoderClassifier
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances




model = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb", 
    savedir="pretrained_models/spkrec-ecapa-voxceleb"
)

def audio_to_embedding(audio_path: str) -> torch.Tensor:
    waveform, sample_rate = sf.read(audio_path)
    # waveform = torch.FloatTensor(waveform)

    # Convert to mono
    if waveform.ndim > 1:
        waveform = waveform.mean(axis=1)

    # resample to 16kHz
    waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=16000)
    sr = 16000

    waveform = nr.reduce_noise(y=waveform, sr=sr)

    # Normalize waveform
    mean = waveform.mean()
    std = waveform.std()
    if std > 0:
        waveform = (waveform - mean) / std
    else:
        waveform = waveform - mean 
    
    waveform = torch.from_numpy(waveform).float()

    with torch.no_grad():
        # Get the embedding (Speaker identity vector)
        embeddings = model.encode_batch(waveform.unsqueeze(0))

    return embeddings.squeeze()

# Define files
audio_files = [
    "contents/Lalji.wav",      
    "contents/m.wav", 
    "contents/Lalji3.wav",  
]


embeddings_list = []
for path in audio_files:
    emb = audio_to_embedding(path)
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
