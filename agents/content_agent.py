import json
import os
import re
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import numpy as np

class ContentCreatorAgent:
    def __init__(self):
        # 1. Load the Content Data Dataset (Templates)
        data_path = os.path.join(os.getcwd(), 'data', 'content_formats.json')
        with open(data_path, 'r') as f:
            self.dataset = json.load(f)

        # 2. Load the "Brain" for intent matching
        model_path = './tuned_model_v1' if os.path.exists('./tuned_model_v1') else 'all-MiniLM-L6-v2'
        self.brain = SentenceTransformer(model_path)

        # 3. Load the Local Text-Generation-Model (DistilGPT2)
        # (This is used for polishing, with a strong safety fallback)
        print("DEBUG: Loading local Text-Generation-Model (DistilGPT2)...")
        self.generator = pipeline('text-generation', model='distilgpt2')

    def create_content(self, user_query):
        # A. INTENT DECODING (Selecting the Template)
        categories = list(self.dataset.keys())
        # Represent categories by their names and tones
        category_prompts = [f"{self.dataset[cat]['title']} {self.dataset[cat]['tone']}" for cat in categories]
        cat_embeddings = self.brain.encode(category_prompts, convert_to_tensor=True)
        query_embedding = self.brain.encode(user_query, convert_to_tensor=True)
        similarities = util.cos_sim(query_embedding, cat_embeddings)[0].cpu().numpy()
        best_cat_idx = np.argmax(similarities)
        best_category = categories[best_cat_idx]
        template = self.dataset[best_category]['structure']

        # B. INFORMATION EXTRACTION (Slot Filling)
        # 1. We look for the "To" person (e.g., Principal)
        # Pattern: (to|for the) [X] (because|due to)
        match_recipient = re.search(r'(?i)(?:to|for the) ([\w\s]+) (?:because|due to|since)', user_query)
        recipient = match_recipient.group(1).strip().title() if match_recipient else "Principal/Manager"

        # 2. We look for the "Reason" (e.g., high fever)
        # Pattern: (because|due to|since) [X]
        match_reason = re.search(r'(?i)(?:because|due to|since) ([\w\s.,!]+)', user_query)
        clean_reason = match_reason.group(1).strip().lower() if match_reason else user_query

        # C. AI POLISHING & HALLUCINATION FILTER
        # This is where we stop the "giant btw" and "1 2 3" bugs.
        human_prompt = f"Topic: {clean_reason}\nFriendly Formal Phrase:"
        
        try:
            # Short generation with tight constraints
            polished_result = self.generator(human_prompt, max_new_tokens=30, repetition_penalty=2.0, temperature=0.6, truncation=True)
            ai_phrase = polished_result[0]['generated_text'].split("Phrase:")[-1].strip().split(".")[0] + "."
            
            # THE "RAMBLING FILTER"
            # If the AI says something bizarre (like giant, 123, Input, etc)
            is_bad_output = any(word in ai_phrase.lower() for word in ["btw", "giant", "input", "output", "money", "business", ":"])
            digit_count = sum(c.isdigit() for c in ai_phrase)
            
            if is_bad_output or digit_count > 5 or len(ai_phrase) < 10:
                # FALLBACK TO HUMAN-QUALITY DEFAULT (Safest + Professional)
                polished_reason = f"I am currently facing {clean_reason} and require some time off to recover."
            else:
                polished_reason = ai_phrase
        except:
            polished_reason = f"I am dealing with {clean_reason} and wish to request a formal leave."

        # D. FINAL TEMPLATE FILLING (Actually Replacing Info)
        final_content = template
        # Dynamic Replacements (REPLACES THE BRACKETS)
        final_content = final_content.replace("[RECIPIENT_NAME]", recipient)
        final_content = final_content.replace("[RECIPIENT_TITLE]", recipient if recipient != "Principal/Manager" else "Management")
        final_content = final_content.replace("[REASON]", polished_reason)
        final_content = final_content.replace("[TOPIC]", clean_reason[:30].title())
        
        # Static Placeholders for Manual Editing
        placeholders = {
            "[SALUTATION]": "Sir/Madam",
            "[YOUR_NAME]": "(Your Name)"
        }

        for key, val in placeholders.items():
            final_content = final_content.replace(key, val)

        return f"\n--- [Professional Document | Tone: {self.dataset[best_category]['tone']}] ---\n\n{final_content}"

# Global instance
content_creator_v2 = ContentCreatorAgent()

def content_agent(query):
    return content_creator_v2.create_content(query)
