import torch
import soundfile as sf
import torchaudio
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from transformers import WavLMModel, Wav2Vec2FeatureExtractor

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SAMPLE_RATE = 16000

# Load feature extractor & model
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(
    "microsoft/wavlm-base-plus-sv"
)
model = WavLMModel.from_pretrained(
    "microsoft/wavlm-base-plus-sv"
).to(DEVICE)
model.eval()


def load_audio(path):
    audio, sr = sf.read(path)

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    if sr != SAMPLE_RATE:
        audio = torchaudio.functional.resample(
            torch.tensor(audio), sr, SAMPLE_RATE
        ).numpy()

    return audio


def extract_embedding(audio):
    inputs = feature_extractor(
        audio,
        sampling_rate=SAMPLE_RATE,
        return_tensors="pt",
        padding=True
    )

    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling
    emb = outputs.last_hidden_state.mean(dim=1)

    # L2 normalize
    emb = torch.nn.functional.normalize(emb, dim=1)

    return emb.cpu().numpy()


# Test
audio1 = load_audio("contents/Lalji.wav")
audio2 = load_audio("contents/aggresive.wav")

emb1 = extract_embedding(audio1)
emb2 = extract_embedding(audio2)

score = cosine_similarity(emb1, emb2)[0][0]
print("Cosine similarity:", score)
print("Euclidian distance :", euclidean_distances(emb1, emb2)[0][0])
