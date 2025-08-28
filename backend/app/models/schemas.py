from pydantic import BaseModel, Field
from typing import List, Dict, Any

# --- Request Schemas ---

class QARequest(BaseModel):
    """
    Defines the shape of the incoming request for the /ask endpoint.
    """
    question: str = Field(
        ..., 
        min_length=3, 
        max_length=200,
        description="The question to be answered by the QA bot."
    )

# --- Response Schemas ---

class Source(BaseModel):
    """
    Defines the shape of a single source document.
    """
    content: str
    metadata: Dict[str, Any]

class QAResponse(BaseModel):
    """
    Defines the shape of the outgoing response from the /ask endpoint.
    """
    answer: str
    sources: List[Source]