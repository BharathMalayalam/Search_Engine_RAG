import sys
import os
from dotenv import load_dotenv

# Ensure the root is in the path
sys.path.append(os.getcwd())

from agents.research_agent import research_agent
from agents.email_agent import email_agent

load_dotenv(override=True)

topic = "Climate Change"
email = "bharathmalayalam25@gmail.com"

print(f"DEBUG: Running test for topic: '{topic}' to email: '{email}'")

try:
    content = research_agent(topic)
    print(f"DEBUG: Research content generated: {content[:100]}...")
    
    email_agent(email, content)
    print("DEBUG: email_agent executed successfully.")
except Exception as e:
    print(f"DEBUG: EXECUTION FAILED: {e}")
