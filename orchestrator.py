import os
import torch
from agents.brain_model import DeepIntentBrain, INTENT_LABELS
from sentence_transformers import SentenceTransformer
from agents.research_agent import research_agent
from agents.email_agent import email_agent
from agents.content_agent import content_agent

# Initialize the Brain and its Feature Extractor
base_model = SentenceTransformer('all-MiniLM-L6-v2')
# Load the Deep Neural Brain (Frontal Lobe)
brain_path = './agents/brain_memory.pth'
# 3 classes: 0: research, 1: content, 2: emergency
brain = DeepIntentBrain(num_classes=3)
if os.path.exists(brain_path):
    brain.load_state_dict(torch.load(brain_path))
brain.eval() # Set to evaluation mode

import json

from agents.multi_source_agent import multi_source_agent

def orchestrator(topic, email, send_email=False, mode='research', profile=None, super_agent=False):
    # STEP 0: NEURAL MEMORY RECALL
    log_path = os.path.join(os.getcwd(), 'data', 'learning_log.json')
    log = {"queries": []} # Default value for the next step context
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            try:
                log = json.load(f)
                for past in log.get('queries', []):
                    if past['topic'].lower() == topic.lower():
                        final_output = past['content'] + "\n\n(Memory Recall)"
                        if send_email and email: email_agent(email, final_output)
                        return final_output
            except: pass

    # Use the Super Agent if requested
    if super_agent:
        print(f"DEBUG: ROUTING TO SUPER AGENT for topic: {topic}")
        final_output = multi_source_agent(topic, profile or {})
    else:
        # STEP 1: THE NEURAL BRAIN DECISION...
        with torch.no_grad():
            embedding = base_model.encode(topic, convert_to_tensor=True).detach().clone()
            prediction = brain(embedding.unsqueeze(0))
            intent_index = torch.argmax(prediction).item()
            detected_intent = INTENT_LABELS.get(intent_index, "research")
        
        print(f"DEBUG BRAIN: Detected Intent = {detected_intent.upper()}")

        if mode == 'content' or detected_intent in ['content', 'emergency']:
            final_output = content_agent(topic)
        else:
            final_output = research_agent(topic)
    
    if send_email and email:
        email_agent(email, final_output)
    
    # STEP 2: AUTOMATIC NEURAL LEARNING (CACHING)
    # If the topic was not in memory, save it now so it is "known" for next time.
    try:
        if not any(past['topic'].lower() == topic.lower() for past in log.get('queries', [])):
            log['queries'].append({"topic": topic, "content": final_output})
            with open(log_path, 'w') as f:
                json.dump(log, f, indent=2)
            print(f"DEBUG BRAIN: Query '{topic}' saved to memory for future recall.")
    except Exception as e:
        print(f"DEBUG BRAIN Error: Could not update memory log: {e}")

    return final_output