import torch
import torch.nn as nn
import torch.optim as optim
from sentence_transformers import SentenceTransformer
from agents.brain_model import DeepIntentBrain
import os

# 1. Load the Sentence-Transformer Brain (for embeddings)
# We use this as our initial "feature extractor"
base_model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. LABELED DATASET FOR "HUMAN-BRAIN" TRAINING
# 0: Research, 1: Content Creator (Letters), 2: Emergency
train_data = [
    ("Tell me about the history of India", 0),
    ("Who is the actor Ajith Kumar?", 0),
    ("Information about climate change", 0),
    ("Give me research notes on machine learning", 0),
    ("Science behind global warming", 0),
    ("Write a leave letter to principal", 1),
    ("Draft a permission letter for the office", 1),
    ("I need a formal application for a day off", 1),
    ("Create a request to attend a seminar", 1),
    ("Compose an email asking for a vacation", 1),
    ("This is an emergency medical leave request", 2),
    ("Urgent: I have had an accident and need time off", 2),
    ("I am suffering from high fever and need urgent help", 2),
    ("Please grant an immediate permission for emergency", 2)
]

# 3. CONVERT TO EMBEDDINGS (The "Neural Inputs")
print("--- [1] PREPARING NEURAL INPUTS ---")
# Clone the embeddings to ensure they are compatible with standard training
embeddings = base_model.encode([item[0] for item in train_data], convert_to_tensor=True)
X = embeddings.detach().clone()
y = torch.tensor([item[1] for item in train_data])

# 4. INITIALIZE THE NEW DEEP BRAIN MODEL
brain = DeepIntentBrain(input_dim=X.shape[1], num_classes=3)

# 5. DEFINE THE "LEARNING" PARAMETERS
# CrossEntropyLoss: Measures how much the AI "guesses" wrong
criterion = nn.CrossEntropyLoss()
# Adam Optimizer: A standard human-inspired approach to learning efficiently
optimizer = optim.Adam(brain.parameters(), lr=0.001)

# 6. THE TRAINING LOOP (The "Fine-Tuning" Process)
print("\n--- [2] TRAINING MULTIPLE HIDDEN LAYERS ---")
# Training for multiple epochs to ensure the brain "understands" deep patterns
for epoch in range(100):
    optimizer.zero_grad()
    outputs = brain(X)
    loss = criterion(outputs, y)
    loss.backward()
    optimizer.step()
    
    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/100], Learning Loss: {loss.item():.4f}")

# 7. SAVE THE BRAIN'S MEMORY
model_save_path = './agents/brain_memory.pth'
torch.save(brain.state_dict(), model_save_path)
print(f"\n✅ SUCCESS: Deep Brain Fine-Tuned and saved to: {model_save_path}")
print("Your Search Engine is now powered by a multi-layered Neural Network.")
