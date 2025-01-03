# app/routers/api.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.models.pdf_processor import PDFProcessor
from app.models.embeddings_manager import (
    EmbeddingsManager,
    add_pdf_summary,
    query_pdf_summaries,
    get_summary_collection,
    delete_pdf_data,
)
from app.models.question_answering import QuestionAnswering
from app.utils.logger import get_logger
from app.utils.config import Config
from fastapi.responses import JSONResponse, RedirectResponse
from ..schemas import (
    PDFUploadResponse,
    AskQuestionRequest,
    AskQuestionResponse,
    SummaryResponse,
    HealthResponse,
    PDFSummary,
    PurgePDF,
)
from chromadb import Client
from typing import List
import os
import uuid
from pathlib import Path
import shutil

logger = get_logger(__name__)
router = APIRouter()


@router.post("/upload_pdf/", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDFs are allowed."
        )
    try:
        pdf_id = str(uuid.uuid4())
        pdf_name = f"{pdf_id}.pdf"
        os.makedirs("./tmp", exist_ok=True)
        pdf_path = Path("./tmp") / pdf_name

        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        pdf_processor = PDFProcessor()
        question_answering = QuestionAnswering()
        page_texts = pdf_processor.extract_text_from_pdf(pdf_path)
        full_text = pdf_processor.get_full_text(page_texts)
        pdf_summary = question_answering.get_summary(full_text)

        add_pdf_summary(pdf_id=pdf_id, summary=pdf_summary)

        text_chunks = pdf_processor.tokenize_text(page_texts)
        embeddings_manager = EmbeddingsManager(pdf_id)
        embeddings_manager.update_embeddings(text_chunks)

        os.remove(pdf_path)

        return PDFUploadResponse(
            message="PDF processed and embeddings updated.",
            pdf_id=pdf_id,
            summary=pdf_summary,
        )
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


@router.post("/ask_questions/", response_model=AskQuestionResponse)
async def ask_questions(req: AskQuestionRequest):
    try:
        pdf_id_to_use = req.pdf_id
        if pdf_id_to_use is None:
            # query pdf_summaries
            if not req.questions:
                raise HTTPException(
                    status_code=400, detail="No question provided and no pdf_id."
                )
            # We'll just use the first question to determine the best pdf
            query = req.questions[0]
            pdf_results = query_pdf_summaries(query, top_k=1)
            if not pdf_results or not pdf_results.get("documents"):
                # No suitable PDF found
                for q in req.questions:
                    answers[q] = {
                        "answer": "Data Not Available",
                        "confidence": None,
                        "source": None,
                    }
                return AskQuestionResponse(answers=answers)

            # Extract the pdf_id from metadata
            pdf_id_to_use = pdf_results["metadatas"][0][0].get("pdf_id")

        question_answering = QuestionAnswering()
        answers = {}

        embeddings_manager = EmbeddingsManager(pdf_id_to_use)

        for question in req.questions:
            results = embeddings_manager.query_embeddings(question)
            if results and results["documents"]:
                top_chunks = results["documents"][0]
                context = "\n\n".join(top_chunks)
                answer = question_answering.get_answer(context, question)
                if answer and answer != "Data Not Available":
                    answers[question] = answer
                else:
                    answers[question] = "Data Not Available"
            else:
                answers[question] = "Data Not Available"
        return JSONResponse(content=answers)
    except Exception as e:
        logger.error(f"Error answering questions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


@router.get("/")
def redirection_route():
    # Redirect the user from "/" to "/docs"
    return RedirectResponse(url="/docs")


@router.get("/health")
def health_check():
    return HealthResponse(status="ok")


@router.get("/existing_pdfs", response_model=List[PDFSummary])
def get_all_pdf_summaries():
    col = get_summary_collection()
    all_data = col.get()  # Retrieve all documents from the pdf_summaries collection
    documents = all_data.get("documents", [])
    metadatas = all_data.get("metadatas", [])

    results = []
    for doc, meta in zip(documents, metadatas):
        pdf_id = meta.get("pdf_id")
        summary = doc
        results.append(PDFSummary(pdf_id=pdf_id, summary=summary))
    return results


@router.post("/purge", response_model=PurgePDF)
def purge_pdf_id(pdf_id: str):
    success = delete_pdf_data(pdf_id)
    if not success:
        raise HTTPException(status_code=404, detail="PDF ID not found")

    return PurgePDF(message=f"Collection '{pdf_id}' deleted successfully")
