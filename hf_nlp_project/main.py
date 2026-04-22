import os
import re
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

# --- REQUIREMENT 1: Setup & Imports ---
print("\n" + "="*40)
print("--- [1] SETUP & IMPORTS ---")
# Using 'all-MiniLM-L6-v2' (State-of-the-Art for embeddings)
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
print(f"Model {MODEL_NAME} loaded successfully.")

# --- REQUIREMENT 2: Dataset Loading (GLUE STSB) ---
print("\n--- [2] LOADING DATASET (GLUE/STSB) ---")
dataset = load_dataset("glue", "stsb")

# Show structure
print(f"Dataset Structure:\n{dataset}")

# --- REQUIREMENT 3: Data Exploration ---
print("\n--- [3] DATA EXPLORATION (First 5 Samples) ---")
# Print first 5 samples from the training set
for i, sample in enumerate(dataset['train'].select(range(5))):
    print(f"Sample {i+1}:")
    print(f"  Sentence 1: {sample['sentence1']}")
    print(f"  Sentence 2: {sample['sentence2']}")
    print(f"  Similarity Score: {sample['label']} (Target Range: 0.0 to 5.0)")

'''
FIELD EXPLANATION:
- sentence1: The first piece of text to compare.
- sentence2: The second piece of text to compare.
- label: A gold target score (0-5) representing how semantically similar the pair is.
'''

# --- REQUIREMENT 4: Preprocessing ---
print("\n--- [4] PREPROCESSING ---")
def clean_text(text):
    text = text.lower() # Lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text) # Remove special characters
    return text.strip()

def get_embeddings(sentences):
    # Pre-clean sentences
    cleaned = [clean_text(s) for s in sentences]
    
    # Tokenize (R4 requirement: Using Transformers)
    encoded_input = tokenizer(cleaned, padding=True, truncation=True, return_tensors='pt')
    
    # Compute embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)
    
    # Perform mean pooling for the best semantic representation
    # This averages across each token's embedding to get a single sentence vector
    sentence_embeddings = model_output.last_hidden_state.mean(dim=1)
    
    # Normalize for easier cosine similarity
    return F.normalize(sentence_embeddings, p=2, dim=1)

# --- REQUIREMENT 5: Core Functionality (OPTION A: Semantic Similarity Tool) ---
print("\n--- [5] CORE SEMANTIC SIMILARITY TOOL ---")

def calculate_similarity(s1, s2):
    embeddings = get_embeddings([s1, s2])
    # Compute cosine similarity (dot product of normalized 1D vectors)
    score = torch.dot(embeddings[0], embeddings[1]).item()
    return round(score * 100, 2) # Return as percentage

# DEMO: Test the tool with custom inputs
test_sentence_a = "The feline is sleeping on the mat"
test_sentence_b = "A cat is resting on the rug"

final_score = calculate_similarity(test_sentence_a, test_sentence_b)

print(f"Input A: '{test_sentence_a}'")
print(f"Input B: '{test_sentence_b}'")
print(f"Total Semantic Match: {final_score}%")
print("="*40 + "\n")
