from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity



sentences = ["नमस्ते दुनिया", "Hello world", "How to open a bank account?", "बैंक खाता कैसे खोलें?"]



model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')
embeddings = model.encode(sentences)
print(embeddings)


print(cosine_similarity(embeddings))
