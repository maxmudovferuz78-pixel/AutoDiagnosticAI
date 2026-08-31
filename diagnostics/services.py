import json
import os
from google import genai
from google.genai import types
from django.conf import settings

# Gemini Client ni sozlaymiz
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


