# src/config.py

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Load API Key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Define the Gemini Model to be used for text generation
MODEL_NAME = "gemini-2.5-flash"