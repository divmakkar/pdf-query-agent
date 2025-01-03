# app/main.py

from fastapi import FastAPI
from app.routers import api
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="PDF Question Answering Agent",
    description="Upload a PDF and enter your questions to receive answers based on the document's content.",
    version="0.0.2",
)

app.include_router(api.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
