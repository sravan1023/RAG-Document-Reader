# routes.py
import os
import sys
import traceback
from pathlib import Path
from threading import Lock

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

# --- Path Fix (leave as-is for now) ---
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Your modules
from app.core.qa_services import qa_service
from scripts.ingest import create_vector_store
from config import settings

api_blueprint = Blueprint("api", __name__)

# --- Config / Globals ---
ALLOWED_EXTENSIONS = {"pdf"}
DATA_DIR = Path(settings.DATA_PATH)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Optional: set in your app factory too (e.g., 50 MB)
# app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

_UPLOAD_LOCK = Lock()  # serialize upload -> ingest -> reload to avoid races


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def looks_like_pdf(file_storage) -> bool:
    """Lightweight magic check: first 5 bytes should be '%PDF-'."""
    pos = file_storage.stream.tell()
    head = file_storage.stream.read(5)
    file_storage.stream.seek(pos)
    return head == b"%PDF-"


def clear_previous_pdfs():
    """Delete only PDFs in the data directory (don’t nuke everything)."""
    for p in DATA_DIR.glob("*.pdf"):
        try:
            p.unlink()
        except Exception:
            current_app.logger.exception(f"Failed deleting {p}")


@api_blueprint.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only .pdf files are allowed."}), 400

    if not looks_like_pdf(file):
        return jsonify({"error": "File does not appear to be a valid PDF."}), 400

    filename = secure_filename(file.filename)
    save_path = DATA_DIR / filename

    # Serialize ingestion to avoid simultaneous index rebuilds
    with _UPLOAD_LOCK:
        try:
            clear_previous_pdfs()
            file.save(save_path)

            # Build/replace vector store on disk.
            # (Assumes create_vector_store reads from settings.DATA_PATH.)
            create_vector_store()

            # Reload in-memory index
            qa_service.reload_vector_store()

            return jsonify({"message": f"File '{filename}' uploaded and processed successfully."}), 200

        except Exception as e:
            current_app.logger.error("Failed to process file")
            current_app.logger.error(traceback.format_exc())
            return jsonify({"error": f"Failed to process file: {str(e)}"}), 500


@api_blueprint.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question")
    k = data.get("k")  # optional override for top-k retrieval

    if not question or not isinstance(question, str):
        return jsonify({"error": "Missing 'question' (string) in request body"}), 400

    try:
        result = qa_service.answer_question(question, top_k=k) if k else qa_service.answer_question(question)
        return jsonify(result), 200
    except Exception:
        current_app.logger.error("Error in /ask")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": "An internal error occurred."}), 500
