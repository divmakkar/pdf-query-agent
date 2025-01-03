from pydantic import BaseModel
from typing import Optional, List, Dict


class PDFUploadResponse(BaseModel):
    message: str
    pdf_id: str
    summary: str


class AskQuestionRequest(BaseModel):
    questions: List[str]
    pdf_id: Optional[str] = None
    top_k: Optional[int] = 3


class AskQuestionResponse(BaseModel):
    answers: Dict[str, Dict]  # {question: {answer, confidence, source}}


class SummaryResponse(BaseModel):
    summary: str


class HealthResponse(BaseModel):
    status: str


class PDFSummary(BaseModel):
    pdf_id: str
    summary: str


class PurgePDF(BaseModel):
    message: str
