# app/models/embeddings_manager.py

import chromadb
from chromadb.utils import embedding_functions
from app.utils.config import Config
from app.utils.logger import get_logger
import openai

logger = get_logger(__name__)


class EmbeddingsManager:
    def __init__(self, pdf_id):
        self.client = chromadb.PersistentClient(path=Config.CHROMADB_PERSIST_DIR)
        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=Config.OPENAI_API_KEY, model_name=Config.EMBEDDING_MODEL_NAME
        )
        self.collection = self.client.get_or_create_collection(
            name=pdf_id, embedding_function=self.openai_ef
        )

    def update_embeddings(self, text_chunks):
        try:
            ids = [chunk["chunk_id"] for chunk in text_chunks]
            documents = [chunk["text"] for chunk in text_chunks]
            metadatas = [
                {"chunk_id": chunk["chunk_id"], "page_number": chunk["page_number"]}
                for chunk in text_chunks
            ]
            try:
                self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            except Exception as e:
                logger.error("Error adding documents to collection")
                raise e
            logger.info(f"Embeddings updated for collection {self.collection.name}")
        except Exception as e:
            logger.error(f"Error updating embeddings: {e}")
            raise e

    def query_embeddings(self, question, n_results=3):
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
            return results
        except Exception as e:
            logger.error(f"Error querying embeddings: {e}")
            raise e
