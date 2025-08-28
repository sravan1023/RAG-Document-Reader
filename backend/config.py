# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # --- API KEYS ---
    HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")  # for HF Providers (LLM)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # only if using OpenAI embeddings

    # --- PATHS ---
    DATA_PATH = os.getenv("DATA_PATH", "data/")
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "vector_store/faiss_index")

    # --- LLM (HF Providers) ---
    LLM_REPO_ID = os.getenv("LLM_REPO_ID", "meta-llama/Meta-Llama-3-8B-Instruct")
    LLM_MAX_OUTPUT_TOKENS = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "400"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))

    # --- EMBEDDINGS ---
    # Choose: "openai" (remote) or "local" (Sentence-Transformers)
    EMBEDDINGS_PROVIDER = os.getenv("EMBEDDINGS_PROVIDER", "openai")

    # OpenAI embeddings (modern models)
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-small")
    # You can down-project 3-large/3-small via `dimensions` (e.g., 256/1024/1536/3072)
    EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

    # Local embeddings (CPU-friendly, great quality)
    LOCAL_EMBEDDING_MODEL = os.getenv("LOCAL_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    NORMALIZE_EMBEDDINGS = os.getenv("NORMALIZE_EMBEDDINGS", "true").lower() == "true"

    # --- CHUNKING & RETRIEVAL ---
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
    SEARCH_K = int(os.getenv("SEARCH_K", "5"))
    MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "4000"))  # for prompt packing
    FAISS_METRIC = os.getenv("FAISS_METRIC", "ip")  # 'ip' = inner product (cosine if normalized)

settings = Settings()
