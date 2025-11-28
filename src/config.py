import os

DATA_DIR = os.getenv("DATA_DIR", "data/pdfs")
CHROMA_DIR = os.getenv("CHROMA_DIR", "data/chroma_db")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TOP_K = int(os.getenv("TOP_K", 5))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

