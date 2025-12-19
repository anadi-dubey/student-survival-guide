import google.generativeai as genai
import os

# Paste your API key here to test
api_key = "AIzaSyAyL58F7SuOa1RYUJoR8HrA_SMPdDdKLEI"

genai.configure(api_key=api_key)

print("Searching for available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")