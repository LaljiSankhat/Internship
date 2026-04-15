import tensorflow as tf
import tensorflow_hub as hub


elmo = hub.load("https://tfhub.dev/google/elmo/3")

# print(elmo.signatures)

def get_elmo_embedding(sentences):
    embeddings = elmo.signatures["default"](tf.constant(sentences))["elmo"]
    return embeddings

sentences = [
    "The bank will approve your loan.",
    "He sat by the bank of the river."
]

embeddings = get_elmo_embedding(sentences)
print(embeddings)
print(len(embeddings))
print(len(embeddings[0]))
print(len(embeddings[0][0]))
print(embeddings[0][1])
print(embeddings[1][4])