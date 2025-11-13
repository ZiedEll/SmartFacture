# groq_client.py
from groq import Groq

def get_groq_client():
    api_key = "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"
    return Groq(api_key=api_key)
