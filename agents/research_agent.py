from sentence_transformers import SentenceTransformer, util
import numpy as np
import wikipedia
import re
import os
from agents.serper_agent import serper_search

def research_agent(query):
    query = query.strip()
    print(f"DEBUG: Performing local ML research using Wikipedia for topic: '{query}'")
    
    # 1. Real Search Option (Serper API)
    serper_results = serper_search(query)
    all_content = ""
    if serper_results:
        print("DEBUG: Using Serper API for Real-World Knowledge...")
        all_content = " ".join(serper_results)
    
    # 2. Local Fallback (Wikipedia)
    if not all_content:
        print("DEBUG: Falling back to Wikipedia...")
        try:
            # Search for the most relevant page titles
            search_results = wikipedia.search(query, results=3)
            if search_results:
                # Get the full page content of the most relevant result
                for title in search_results:
                    try:
                        page = wikipedia.page(title)
                        all_content += page.content + " "
                        if len(all_content) > 5000: break
                    except wikipedia.DisambiguationError as e:
                        try:
                            page = wikipedia.page(e.options[0])
                            all_content += page.content + " "
                        except: continue
                    except Exception:
                        continue
        except Exception as e:
            print(f"DEBUG: Wikipedia connection failed: {e}")
            return f"Local ML Research failed due to a connection issue with Wikipedia."

    if not all_content or len(all_content) < 100:
        return "Not enough meaningful research found on Wikipedia for this topic."

    # 3. Fine-Tuned ML Model (Analyzing the Wikipedia data)
    # Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', all_content)
    # Filter short sentences (noise)
    sentences = [s for s in sentences if len(s.strip()) > 50]

    if not sentences:
        return "Enough data was found, but the model could not extract a formatted answer."

    # 3. Fine-Tuned ML Model (Semantic Search)
    # Load a lightweight, powerful transformer model
    # To "Fine-Tune" this model, you can run: model.fit(train_dataloader, epochs=1) 
    # with your own labeled data. Currently, we use a pre-trained semantic model.
    model = SentenceTransformer('./tuned_model_v1')


    # Compute semantic embeddings
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    # ML Calculation: Cosine Similarity between query and knowledge base
    similarity_scores = util.cos_sim(query_embedding, sentence_embeddings)[0].cpu().numpy()
    
    # Select Top 3 precision-matched answers
    top_indices = np.argsort(similarity_scores)[::-1][:3]
    answer_sentences = [sentences[i].strip() for i in top_indices if similarity_scores[i] > 0]
    
    if not answer_sentences:
         return "The ML model analyzed Wikipedia but no specific answer matched your query well."

    return " Bharath Search Engine" + " ".join(answer_sentences)
