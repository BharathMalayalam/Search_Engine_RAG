import torch
import torch.nn as nn
import torch.nn.functional as F

class DeepIntentBrain(nn.Module):
    def __init__(self, input_dim=384, num_classes=3):
        super(DeepIntentBrain, self).__init__()
        # Layer 1: The "Complex Pattern" Hidden Layer
        # It takes the semantic embedding and expands it to 256 neurons
        self.fc1 = nn.Linear(input_dim, 256)
        
        # Layer 2: The "Refinement" Hidden Layer
        # This layer helps the model catch subtle differences (like Research vs Writing)
        self.fc2 = nn.Linear(256, 128)
        
        # Layer 3: The "Sentiment" Hidden Layer
        # This layer helps the brain understand the "Tone" of the query
        self.fc3 = nn.Linear(128, 64)
        
        # Dropout for regularization (Prevents overthinking)
        self.dropout = nn.Dropout(0.2)
        
        # Output Layer: Deciding the final intent
        # 0: Research, 1: Content Writing, 2: Emergency Request
        self.output = nn.Linear(64, num_classes)

    def forward(self, x):
        # Activation Function: ReLU (The standard for human-like neural complexity)
        x = F.relu(self.fc1(x))
        x = self.dropout(F.relu(self.fc2(x)))
        x = F.relu(self.fc3(x))
        
        return self.output(x)

# Mapping of labels for the Brain to understand
INTENT_LABELS = {
    0: "research",
    1: "content", 
    2: "emergency"
}
