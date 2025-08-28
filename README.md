# RAG Document Reader

RAG-powered PDF Q&A using **FAISS** for retrieval and **Meta Llama-3 8B** (via Hugging Face Providers) for answers. Backend: **Flask** · UI: simple web (static) and optional Vite frontend.

---

## Features

* Upload a **PDF**, split into chunks, embed, and index with **FAISS**
* Ask questions; answers are grounded in retrieved chunks (RAG)
* Returns supporting chunks as **sources**
* Works with HF Providers (server-side HF token), OpenAI or local embeddings

---

## Features

* Upload a **PDF**, split into chunks, embed, and index with **FAISS**
* Ask questions; answers are grounded in retrieved chunks (RAG)
* Returns supporting chunks as **sources**
* Works with HF Providers (server-side HF token), OpenAI or local embeddings

---

## Quickstart

### 1) Clone & env

```bash
git clone [https://github.com/sravan1023/RAG-Document-Reader.git](https://github.com/sravan1023/RAG-Document-Reader.git)
cd RAG-Document-Reader
cp .env.example .env  # then fill in your keys (see “Environment” below)
```

On Windows PowerShell:

```powershell
copy .env.example .env
```

### 2) Python setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Run the backend (Flask API)

```bash
python backend/main.py
# API at http://localhost:5000
```

### 4) Use the UI

**Option A (static):** open `web/index.html` in your browser

**Option B (Vite frontend):**

```bash
cd frontend
npm install
npm run dev
# open the shown localhost URL
```

---

## API

#### `POST /api/upload`

Upload a PDF, index it, and reload the vector store.

**Body:** `multipart/form-data` with field `file` (PDF)

**Response:**

```json
{ "message": "File 'your.pdf' uploaded and processed successfully." }
```

#### `POST /api/ask`

Ask a question about the indexed PDF.

**Body (JSON):**

```json
{ "question": "Your question here", "k": 5 }  // k optional
```

**Response:**

```json
{
  "answer": "Short grounded answer…",
  "sources": [
    { "content": "chunk text…", "metadata": { "page": 3, "...": "..." } }
  ]
}
```

---

## Environment

Create `.env`. Example:

```ini
HUGGINGFACEHUB_API_TOKEN=hf_********************************
OPENAI_API_KEY=sk_********************************
LLM_REPO_ID=meta-llama/Meta-Llama-3-8B-Instruct

# Retrieval & embeddings (defaults shown)
EMBEDDINGS_PROVIDER=openai    # or local
EMBEDDING_MODEL_NAME=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# Paths
DATA_PATH=data/
VECTOR_STORE_PATH=vector_store/faiss_index

# Chunking & retrieval
CHUNK_SIZE=1000
CHUNK_OVERLAP=120
SEARCH_K=5
MAX_CONTEXT_CHARS=4000

# Generation
LLM_TEMPERATURE=0.1
LLM_MAX_OUTPUT_TOKENS=400
```

Tokens stay server-side only. `.gitignore` excludes `.env` already.

---

## Project Structure

```bash
/RAG_PDF/
|
|-- .gitignore
|-- README.md
|-- LICENSE
|
|-- backend/
|   |-- app/
|   |   |-- api/routes.py
|   |   |-- core/qa_services.py
|   |   `-- models/schemas.py
|   |-- data/
|   |   `-- .gitkeep
|   |-- scripts/
|   |   `-- ingest.py
|   |-- vector_store/
|   |   `-- .gitkeep
|   |-- .env
|   |-- config.py
|   |-- main.py
|   `-- requirements.txt
|
|-- frontend/
|   |-- src/
|   |   |-- App.jsx
|   |   |-- index.css
|   |   `-- main.jsx
|   |-- index.html
|   |-- package.json
|   `-- ...
|
`-- web/
    `-- index.html  # Simple static UI option
```



## License

MIT License

Copyright (c) 2025 [Sravan]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Acknowledgements

* FAISS (Facebook AI Similarity Search)
* Meta Llama 3 (via Hugging Face Providers)
* LangChain, Flask
