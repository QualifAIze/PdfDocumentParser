from datetime import datetime
from typing import Dict

from pydantic import BaseModel


class PDFResponse(BaseModel):
    original_file_name: str
    toc: Dict
    toc_with_content: Dict
    created_at: datetime = datetime.now()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
