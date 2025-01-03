# app/models/embeddings_manager.py

import chromadb
from chromadb.utils import embedding_functions
from app.utils.config import Config
from app.utils.logger import get_logger
from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)
client = chromadb.PersistentClient(path=Config.CHROMADB_PERSIST_DIR)


class EmbeddingsManager:
    def __init__(self, pdf_id):
        self.client = client
        self.collection = self.client.get_or_create_collection(
            name=pdf_id,
            embedding_function=embedding_functions.DefaultEmbeddingFunction(),
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


def get_summary_collection():
    return client.get_or_create_collection(name="pdf_summaries")


def add_pdf_summary(pdf_id: str, summary: str):
    col = get_summary_collection()
    # Use pdf_id as id, summary as document
    # metadata includes pdf_id
    col.add(documents=[summary], metadatas=[{"pdf_id": pdf_id}], ids=[pdf_id])


def query_pdf_summaries(query: str, top_k: int = 1):
    col = get_summary_collection()
    results = col.query(query_texts=[query], n_results=top_k)
    return results


def delete_pdf_data(pdf_id: str) -> bool:
    # delete pdf id from summaries and collection

    collection = get_summary_collection()
    existing_items = collection.get(ids=[pdf_id])

    if not existing_items["ids"]:
        return False

    # Delete the PDF summary and associated embeddings
    collection.delete(ids=[pdf_id])

    # now the chunks db

    # List existing collections
    collections = client.list_collections()
    collection_names = [col.name for col in collections]
    # Check if the collection exists
    if pdf_id not in collection_names:
        return False

    # Delete the collection
    client.delete_collection(name=pdf_id)
    return True
