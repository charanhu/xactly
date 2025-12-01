# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG = True

# OpenAI Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

# ChromaDB Configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./kb_index")
CHROMA_COLLECTION_NAME = "customer_support_kb"

# Data Configuration
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")

# Ensure paths exist
Path(CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)
Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)

# Agent Configuration
AGENT_TEMPERATURE = 0.7
AGENT_MAX_TOKENS = 1024

# Knowledge Base Configuration
KB_CHUNK_SIZE = 1000
KB_CHUNK_OVERLAP = 200
KB_SEARCH_RESULTS = 5

# Session Configuration
MAX_CHAT_HISTORY = 50
SESSION_TIMEOUT_MINUTES = 30
