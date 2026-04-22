from sentence_transformers import SentenceTransformer, InputExample, losses
from datasets import load_dataset
from torch.utils.data import DataLoader
import os
import torch

# 1. Load the base model
# 'all-MiniLM-L6-v2' is lightweight but surprisingly powerful after tuning.
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. LOAD A REAL-WORLD RESEARCH DATASET (GLUE STSB)
# Expert-labeled similarity scores (0.0 to 5.0) for thousands of pairs.
print("\n" + "="*40)
print("--- [1] LOADING GLUE/STSB DATASET ---")
stsb_data = load_dataset("glue", "stsb")

# 3. PREPARE INPUT EXAMPLES
# Normalize STSB labels (0-5) into 0.0-1.0 (expected by CosineSimilarityLoss)
train_examples = []
for row in stsb_data['train']:
    train_examples.append(InputExample(
        texts=[row['sentence1'], row['sentence2']],
        label=row['label'] / 5.0
    ))

print(f"Dataset Loaded: {len(train_examples)} research pairs ready for training.")

# 4. DATALOADER & LOSS FUNCTION
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)

# 5. START DEEP FINE-TUNING
# We overwrite 'tuned_model_v1' so the 'research_agent.py' picks it up immediately.
output_path = './tuned_model_v1'

print("\n--- [2] STARTING DEEP FINE-TUNING ---")
print("Tuning your 'Bharath Search Engine' on top-tier NLP data...")
print("Please wait, this will take about 1-2 minutes on typical CPUs.")

try:
    model.fit(
        train_objectives=[(train_dataloader, train_loss)], 
        epochs=1, # One pass through 5,000+ examples gives a huge upgrade
        warmup_steps=100, 
        output_path=output_path
    )
    print("\n" + "="*40)
    print(f"✅ SUCCESS: Fine-Tuning Complete!")
    print(f"Your model is now smarter and saved to: {output_path}")
    print("="*40 + "\n")

except Exception as e:
    print(f"ERROR: Fine-tuning failed: {e}")
