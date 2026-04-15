import torch
import torchaudio
from sklearn.metrics.pairwise import cosine_similarity

model = torch.hub.load("PalabraAI/redimnet2", "redimnet2", model_name="b6", train_type="lm", pretrained=True)
model.eval()

waveform, sr = torchaudio.load("audios/Lalji.m4a")
waveform2, sr2 = torchaudio.load("audios/m2.mp3")
# waveform: (batch, samples), 16 kHz
with torch.no_grad():
    embedding = model(waveform)  # (batch, emb_dim)
    embedding2 = model(waveform2)  # (batch, emb_dim)

# similarity between the two embeddings
similarity = cosine_similarity(embedding, embedding2)
print(similarity)