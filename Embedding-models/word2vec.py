from curses import window
from gensim.models import Word2Vec
import gensim
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
nltk.download('punkt_tab')
import zipfile

cleaned_text = None

with zipfile.ZipFile("Gutenburg.zip", 'r') as zip_ref:
    file_name = zip_ref.namelist()[0]
    with zip_ref.open(file_name) as file:
        content = file.read().decode('utf-8', errors='ignore')
        cleaned_text = content.replace("\n", " ")
        print("File loaded")

print(len(cleaned_text))


data = []

for i in sent_tokenize(cleaned_text):
    temp = []
    for j in word_tokenize(i):
        temp.append(j.lower())
    data.append(temp)

print(len(data))


# CBOW model
model1 = gensim.models.Word2Vec(data, min_count=1, vector_size=100, window=5)

# skip grams   using sg = 1
model2 = gensim.models.Word2Vec(data, min_count=1, vector_size=100, window=5, sg=1)  

print(model1.wv.similarity('alice', 'wonderland'))
print(model2.wv.similarity('alice', 'machines'))


# to check embedding of word
# print(model2.wv["deep"]) 



# similar words of given word   
# print(model2.wv.most_similar("alice", topn=5))
# model2.wv.most_similar("alice")
