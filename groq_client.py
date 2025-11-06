# groq_client.py
from groq import Groq

def get_groq_client():
    api_key = "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"
    return Groq(api_key=api_key)
