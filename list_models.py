#!/usr/bin/env python3
"""
List available Gemini models
"""

import os

# Set environment variable
os.environ['GEMINI_API_KEY'] = 'AIzaSyDhnw1xyPaWa6rfi0ZacwTaPt6SEsPZGP4'

try:
    import google.generativeai as genai
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    
    print("🔍 Available Gemini models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
    
except Exception as e:
    print(f"❌ Error: {e}")