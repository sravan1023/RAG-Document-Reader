import os, sys
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient, HfApi, login

# --- Path Fix ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
# --- End Path Fix ---

load_dotenv(Path(project_root) / ".env", override=True)

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from config import settings


class QAService:
    def __init__(self):
        print("Initializing QA Service with Hugging Face…")

        # --- Embeddings (OpenAI) ---
        # Ensure OPENAI_API_KEY is set if you use OpenAI embeddings
        if not os.getenv("OPENAI_API_KEY"):
            print("OPENAI_API_KEY not set; OpenAIEmbeddings will fail if called.")
        self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL_NAME)
        
        hf_token = (
            os.getenv("HUGGINGFACEHUB_API_TOKEN")
            or os.getenv("HF_TOKEN")
            or os.getenv("HUGGING_FACE_HUB_TOKEN")   # legacy var name fallback
        )
        if not hf_token or not hf_token.startswith("hf_"):
            raise ValueError(
                "Hugging Face token missing/invalid. Put HUGGINGFACEHUB_API_TOKEN=hf_... in .env"
            )
        
        os.environ["HF_TOKEN"] = hf_token
        os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token
        login(token=hf_token) 
        HfApi().whoami()


        # InferenceClient: prefer `api_key` arg name; `token` still works but api_key is clearer.
        self.llm = InferenceClient(
            api_key=hf_token,
            timeout=120,
        )

        self.db = None
        self.retriever = None
        self.reload_vector_store()

    def reload_vector_store(self):
        print("Reloading vector store…")
        if os.path.exists(settings.VECTOR_STORE_PATH):
            self.db = FAISS.load_local(
                settings.VECTOR_STORE_PATH,
                self.embeddings,
                allow_dangerous_deserialization=True,  # OK if you trust the artifact
            )
            self.retriever = self.db.as_retriever(
                search_type="similarity",
                search_kwargs={"k": settings.SEARCH_K},
            )
            print("Vector store reloaded and retriever is ready.")
        else:
            print("No vector store found. Please upload a PDF to create one.")
            self.retriever = None

    def _hf_chat(self, prompt: str) -> str:
        """Call HF Providers (Chat Completions)."""
        try:
            resp = self.llm.chat.completions.create(
                model=settings.LLM_REPO_ID,  # e.g. "meta-llama/Meta-Llama-3-8B-Instruct"
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Answer using the CONTEXT first and keep it friendly and concise. "
                            "If the CONTEXT doesn’t cover something, say so and give a quick pointer instead of guessing. "
                            "Citations like [1] are optional when chunks are numbered. No step-by-step reasoning in the reply."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.LLM_MAX_OUTPUT_TOKENS if hasattr(settings, "LLM_MAX_OUTPUT_TOKENS") else 400,
                temperature=settings.LLM_TEMPERATURE if hasattr(settings, "LLM_TEMPERATURE") else 0.1,
            )
            # Standard extraction
            return resp.choices[0].message.content
        except HfHubHTTPError as e:
            code = getattr(getattr(e, "response", None), "status_code", None)
            if code == 401:
                raise RuntimeError("HF 401 Unauthorized: check your token/env var.") from e
            if code == 403:
                raise RuntimeError(
                    "HF 403 Forbidden: token lacks Providers permission OR you haven't accepted the model's gated license, "
                    "OR this model isn’t available on Providers for your account."
                ) from e
            raise RuntimeError(f"HF error {code or ''}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"HF chat call failed: {e}") from e

    def _pack_context(self, docs, limit_chars: int = 4000) -> str:
        """Pack top-k chunks into ~limit_chars to avoid overlong prompts."""
        max_chars = getattr(settings, "MAX_CONTEXT_CHARS", limit_chars)
        parts, used = [], 0
        for d in docs:
            t = d.page_content.strip()
            if used + len(t) + 2 > max_chars:
                break
            parts.append(t)
            used += len(t) + 2
        return "\n\n".join(parts)

    def answer_question(self, question: str) -> dict:
        if not self.retriever:
            return {
                "answer": "The document has not been processed yet. Please upload a PDF first.",
                "sources": [],
            }

        print(f"Received question: {question}")

        # LangChain ≥0.2: use invoke()
        docs = self.retriever.invoke(question)
        context = self._pack_context(docs)

        prompt = (
            "Use the following context to answer the question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
        )

        answer = self._hf_chat(prompt) or ""

        sources = [{"content": d.page_content, "metadata": d.metadata} for d in docs]
        return {"answer": answer.strip(), "sources": sources}


# Singleton instance
qa_service = QAService()
