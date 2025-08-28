# scripts/ingest.py
import os
import sys
import glob
from pathlib import Path
from typing import List

# --- Path Fix ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# --- End Path Fix ---

from dotenv import load_dotenv
load_dotenv(Path(project_root) / ".env", override=True)

# Updated LC community imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from config import settings


def _find_pdfs(data_dir: str, specific: str | None = None) -> list[str]:
    if specific:
        return [specific] if specific.lower().endswith(".pdf") and os.path.exists(specific) else []
    return sorted(glob.glob(os.path.join(data_dir, "*.pdf")))

def create_vector_store(pdf_path: str | None = None) -> None:
    """
    Process PDF(s), embed chunks, and persist a FAISS index to disk.
    If pdf_path is provided, only that file is processed.
    """
    print("Starting the data ingestion process…")

    # --- sanity: keys/paths ---
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not set — required for OpenAIEmbeddings.")

    data_dir = settings.DATA_PATH
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.VECTOR_STORE_PATH).mkdir(parents=True, exist_ok=True)

    # --- load PDFs ---
    pdf_files = _find_pdfs(data_dir, specific=pdf_path)
    if not pdf_files:
        msg = f"No PDF files found in '{data_dir}'" if not pdf_path else f"PDF not found or invalid: {pdf_path}"
        raise FileNotFoundError(msg)

    documents: List[Document] = []
    print(f"Found {len(pdf_files)} PDF file(s) to process.")
    for pf in pdf_files:
        try:
            loader = PyPDFLoader(pf)
            docs = loader.load()  # returns per-page Documents with metadata
            documents.extend(docs)
            print(f"  ✓ Loaded: {os.path.basename(pf)} ({len(docs)} pages)")
        except Exception as e:
            raise RuntimeError(f"Error loading {os.path.basename(pf)}: {e}") from e

    if not documents:
        raise RuntimeError("No documents were successfully loaded.")

    # --- split to chunks ---
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)
    print(f"Split {len(documents)} page docs into {len(chunks)} text chunks.")

    # --- embeddings (OpenAI v3 models recommended) ---
    # You can expose EMBEDDING_DIMENSIONS in settings (e.g., 1536/1024/256)
    emb_kwargs = {}
    if hasattr(settings, "EMBEDDING_DIMENSIONS") and settings.EMBEDDING_DIMENSIONS:
        emb_kwargs["dimensions"] = settings.EMBEDDING_DIMENSIONS

    print(f"Initializing embeddings model: {settings.EMBEDDING_MODEL_NAME}"
          + (f" (dims={emb_kwargs['dimensions']})" if "dimensions" in emb_kwargs else ""))
    embeddings = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL_NAME,
        **emb_kwargs
    )

    # --- build FAISS ---
    print("Creating FAISS vector store from chunks…")
    vector_store = FAISS.from_documents(chunks, embeddings)

    # --- persist ---
    vector_store.save_local(settings.VECTOR_STORE_PATH)
    print(f"Vector store saved at: {settings.VECTOR_STORE_PATH}")

if __name__ == "__main__":
    # Optional CLI arg: python scripts/ingest.py path/to/file.pdf
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    create_vector_store(pdf_path=arg)
