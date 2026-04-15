# importing libraries
import random
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

# Set a random seed
random_seed = 42
random.seed(random_seed)

# Set a random seed for PyTorch (for GPU as well)
torch.manual_seed(random_seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(random_seed)


# Load BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')


# Input text
texts = ["GeeksforGeeks is a computer science portal", "Hello this is a bert embedding"]

# Tokenize and encode text using batch_encode_plus
# The function returns a dictionary containing the token IDs and attention masks
encoding = tokenizer.batch_encode_plus(texts,# List of input texts
    padding=True,              # Pad to the maximum sequence length
    truncation=True,           # Truncate to the maximum sequence length if necessary
    return_tensors='pt',      # Return PyTorch tensors
    add_special_tokens=True    # Add special tokens CLS and SEP
)

input_ids = encoding['input_ids'] 
attention_mask = encoding['attention_mask']  # Attention mask



print(f"Input IDs:\n{input_ids}")
print(f"Attention Mask:\n{attention_mask}")


print(encoding)


outputs = model(
    input_ids=input_ids,
    attention_mask=attention_mask
)

print(outputs)
print(len(outputs.last_hidden_state))
print(len(outputs.last_hidden_state[0]))
print(len(outputs.last_hidden_state[0][0]))


