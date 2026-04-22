import requests
import os
import json

def serper_search(query):
    """
    Performs a real Google search using the Serper.dev API.
    Returns snippets from the search results.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print("DEBUG: SERPER_API_KEY not found in environment variables.")
        return []

    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "num": 5
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        results = response.json()
        
        snippets = []
        # Organic results
        if "organic" in results:
            for s in results["organic"]:
                snippets.append(s.get("snippet", ""))
        
        # Knowledge Graph (often has good direct answers)
        if "knowledgeGraph" in results:
            kg = results["knowledgeGraph"]
            snippets.append(f"Knowledge Graph: {kg.get('description', '')}")
            
        return [s for s in snippets if s]
    except Exception as e:
        print(f"DEBUG: Serper search failed: {e}")
        return []

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    print(serper_search("What is the latest news about AI?"))
