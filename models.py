from typing import Dict, List, Any
from pydantic import BaseModel


class PDFResponse(BaseModel):
    document_name: str
    subsections: List[Dict[str, Any]]
    subsections_count: int