import os
import re
import json
import arxiv
import wikipedia
from duckduckgo_search import DDGS
import PyPDF2
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import torch
import re
from agents.serper_agent import serper_search

class MultiSourceAgent:
    def __init__(self):
        self.pdf_dir = os.path.join(os.getcwd(), 'data', 'pdfs')
        if not os.path.exists(self.pdf_dir):
            os.makedirs(self.pdf_dir)
        
        # 1. Load the Semantic Re-Ranker (To pick the BEST research chunks)
        print("DEBUG: Loading Semantic Re-Ranker...")
        self.brain = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 2. Load the Generation Model (Flan-T5: much better at following RAG instructions than GPT2)
        print("DEBUG: Loading Local Synthesis Model (Flan-T5-Base)...")
        # flan-t5-base is ~250M params, much smarter than distilgpt2
        try:
            self.generator = pipeline('text2text-generation', model='google/flan-t5-base', device=-1)
        except Exception:
            print("DEBUG: Falling back to text-generation pipeline for current Transformers version")
            self.generator = pipeline('text-generation', model='google/flan-t5-base', device=-1)

    def search_sources(self, query):
        """Aggregates all raw text from sources"""
        raw_chunks = []
        
        # 1. Serper Search (The "Real Search" Option)
        serper_results = serper_search(query)
        if serper_results:
            print("DEBUG: Using Serper API for Real Search Data...")
            raw_chunks.extend(serper_results)
        else:
            # 2. Wikipedia (Fallback/Otherwise)
            try:
                results = wikipedia.search(query, results=2)
                for title in results:
                    try: page = wikipedia.page(title); raw_chunks.append(page.summary)
                    except: pass
            except: pass

            # 3. ArXiv (Fallback/Otherwise)
            try:
                client = arxiv.Client()
                search = arxiv.Search(query=query, max_results=2)
                for res in client.results(search): 
                    raw_chunks.append(f"{res.title}: {res.summary}")
            except: pass

            # 4. Web (DuckDuckGo Fallback/Otherwise)
            try:
                import warnings
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    from duckduckgo_search import DDGS
                    with DDGS() as ddgs:
                        results = list(ddgs.text(query, max_results=3))
                        for r in results: raw_chunks.append(r['body'])
            except: pass

        # PDFs (Always a fallback if available)
        try:
            if os.path.exists(self.pdf_dir):
                for f_name in os.listdir(self.pdf_dir):
                    if f_name.endswith(".pdf"):
                        with open(os.path.join(self.pdf_dir, f_name), 'rb') as f:
                            text = PyPDF2.PdfReader(f).pages[0].extract_text()
                            raw_chunks.append(text[:500])
                        break
        except: pass

        return raw_chunks

    def re_rank(self, query, chunks):
        """Uses Semantic Search to find the top 3 most relevant sentences"""
        if not chunks: return ""
        
        # Split chunks into sentences
        sentences = []
        for c in chunks:
            sentences.extend(re.split(r'(?<=[.!?]) +', c))
        
        sentences = [s.strip() for s in sentences if len(s) > 30][:20] # Limit to top 20 for speed
        if not sentences: return ""

        # Compute Similarity
        query_emb = self.brain.encode(query, convert_to_tensor=True)
        sent_embs = self.brain.encode(sentences, convert_to_tensor=True)
        scores = util.cos_sim(query_emb, sent_embs)[0].cpu().numpy()
        
        # Pick Top 3
        best_indices = scores.argsort()[::-1][:3]
        return " ".join([sentences[i] for i in best_indices if scores[i] > 0.2])

    def generate_content(self, query, profile):
        # 1. Gather & Filter Knowledge (The RAG Part)
        raw_data = self.search_sources(query)
        context = self.re_rank(query, raw_data)
        
        content_type = profile.get("content_type", "Blog")
        tone = profile.get("tone", "professional")
        audience = profile.get("audience", "student")
        
        # 2. Command-Based Prompt for FLAN-T5 (Prevents Echoing)
        # Added special structural guidance for REAL-LOOKING Letter writing
        if content_type == "Letter":
            prompt = f"""
            Task: Write a complete, professional Formal Letter.
            Request: {query} for a {audience}.
            Format:
            [Date]
            [Recipient Name]
            [Recipient Title]
            
            Dear [Recipient],
            [Professional Body Content based on research: {context}]
            
            Sincerely,
            [Your Name]
            
            Output only the final letter content:
            """
        else:
            prompt = f"Task: Generate a final {tone} {content_type} document for a {audience}. \nTopic: {query} \nResearch Context: {context} \nFinal Document Content:"

        try:
            # 3. Aggressive Repetition Filtering (Fixes the loop/poor output bug)
            output = self.generator(
                prompt, 
                max_new_tokens=400, # Increased for full letters
                min_length=50,
                do_sample=True,
                temperature=0.6,
                repetition_penalty=2.5,
                no_repeat_ngram_size=3,
                truncation=True
            )
            
            final_text = output[0]['generated_text'].strip()
            
            # Clean up potential leading Task headings if model hallucinated them
            final_text = re.sub(r'^(Task:|Context:|Request:|Final Letter Content:|Final Document Content:)', '', final_text, flags=re.IGNORECASE).strip()
            
            # 4. Echo Filter (If model just says "I need a...")
            words = final_text.split()
            unique_words_ratio = len(set(words)) / len(words) if words else 0
            
            if len(final_text) < 30 or unique_words_ratio < 0.3:
                # Fallback to a structured template if the AI fails
                return f"[AI Synthesis Failed - Using Template Mode]\n\nSubject: Leave Request - {query}\n\nDear Class Advisor,\n\nI am writing as a {audience} to request leave due to {query}. I hope you will professionally consider this {content_type} request.\n\nSincerely,\n(Your Name)"

            return f"\n--- [Enhanced Local AI | {content_type}] ---\n\n{final_text}"
            
        except Exception as e:
            return f"Synthesizer Error: {str(e)}\n\nExtracted Research: {context}"

def multi_source_agent(query, profile):
    if not hasattr(multi_source_agent, "agent"):
        multi_source_agent.agent = MultiSourceAgent()
    return multi_source_agent.agent.generate_content(query, profile)
