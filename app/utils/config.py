# app/utils/config.py

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # KEY!
    CHROMADB_PERSIST_DIR = os.getenv("CHROMADB_PERSIST_DIR", "./chroma_db")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))  # tokens in one chunk
    TEMP_PDF_DIR = os.getenv("TEMP_PDF_DIR", "./temp_pdfs")  # Store temp pdfs
    ANSWER_MODEL = "claude-3-5-haiku-20241022"  # or another Claude model variant
    SUMMARY_MODEL = "claude-3-haiku-20240307"  # model to use while creating summary
