# app/routers/api.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.models.pdf_processor import PDFProcessor
from app.models.embeddings_manager import EmbeddingsManager
from app.models.question_answering import QuestionAnswering
from app.utils.logger import get_logger
from app.utils.config import Config
from fastapi.responses import JSONResponse
from typing import List
import os
import uuid
from pathlib import Path

logger = get_logger(__name__)
router = APIRouter()


@router.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDFs are allowed."
        )
    try:
        pdf_id = str(uuid.uuid4())
        pdf_name = f"{pdf_id}.pdf"
        original_filename = file.filename
        os.makedirs("./tmp", exist_ok=True)
        pdf_path = Path("./tmp") / pdf_name

        with open(pdf_path, "wb") as f:
            content = await file.read()
            f.write(content)

        pdf_processor = PDFProcessor()
        page_texts = pdf_processor.extract_text_from_pdf(pdf_path)
        text_chunks = pdf_processor.tokenize_text(page_texts)

        embeddings_manager = EmbeddingsManager(pdf_id)

        embeddings_manager.update_embeddings(text_chunks)

        os.remove(pdf_path)

        return {"message": "PDF processed and embeddings updated.", "pdf_id": pdf_id}
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


@router.post("/ask_questions/")
async def ask_questions(questions: List[str], pdf_id: str):
    try:

        embeddings_manager = EmbeddingsManager(pdf_id)
        if embeddings_manager.collection.count() == 0:
            raise HTTPException(
                status_code=400, detail="No embeddings found for the given PDF."
            )

        question_answering = QuestionAnswering()
        answers = {}

        for question in questions:
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
