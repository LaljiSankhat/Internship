from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances


texts = [
    "I love cats",
    "I love dogs",
    "I love animals",
    "I love sparrow"
]


vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

print(vectorizer.get_feature_names_out())
print(X.toarray())
print(cosine_similarity(X=X))