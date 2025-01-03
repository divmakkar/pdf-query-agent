# app/models/pdf_processor.py

import PyPDF2
import nltk
from app.utils.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)
nltk.download("punkt_tab")


class PDFProcessor:
    def __init__(self):
        pass

    def extract_text_from_pdf(self, pdf_path):
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                page_texts = []
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text:
                        page_texts.append({"page_number": page_num + 1, "text": text})
            return page_texts
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise e

    def tokenize_text(self, page_texts, max_tokens=Config.MAX_TOKENS):
        chunks = []
        chunk_id = 0
        for page in page_texts:
            tokens = nltk.word_tokenize(page["text"])
            for i in range(0, len(tokens), max_tokens):
                chunk_tokens = tokens[i : i + max_tokens]
                chunk_text = " ".join(chunk_tokens)
                chunks.append(
                    {
                        "chunk_id": f"chunk_{chunk_id}",
                        "text": chunk_text,
                        "page_number": page["page_number"],
                    }
                )
                chunk_id += 1
        return chunks

    def get_full_text(self, page_text: dict) -> str:
        full_text = ""
        for page in page_text:
            full_text += page["text"] + " "
        return full_text
