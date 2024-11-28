import os
import json
import gradio as gr
import PyPDF2
import openai
import tiktoken
import chromadb
from chromadb.utils import embedding_functions
import hashlib
import logging

# Set your OpenAI API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError(
        "OpenAI API key not set. Please set the OPENAI_API_KEY environment variable."
    )


def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file and returns a list of page texts with page numbers.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    page_texts = []
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()
        page_texts.append(
            {"page_number": page_num + 1, "text": text}  # Pages are 1-indexed
        )
    return page_texts


def tokenize_text(page_texts, max_tokens=500):
    """
    Splits text into chunks based on token limit and includes page numbers.
    """
    tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
    chunks = []
    chunk_id = 0
    for page in page_texts:
        tokens = tokenizer.encode(page["text"])
        for i in range(0, len(tokens), max_tokens):
            chunk_text = tokenizer.decode(tokens[i : i + max_tokens])
            chunks.append(
                {
                    "chunk_id": f"chunk_{chunk_id}",
                    "text": chunk_text,
                    "page_number": page["page_number"],
                }
            )
            chunk_id += 1
    return chunks


def answer_questions(pdf_file, questions):
    """
    Answers questions based on the content of the uploaded PDF using ChromaDB for semantic search.
    Reuses embeddings and vector store if the PDF hasn't changed.
    """
    global collection

    if pdf_file is None or questions.strip() == "":
        return "Please upload a PDF and enter at least one question."

    try:
        # Compute the hash of the uploaded PDF
        pdf_name = os.path.basename(pdf_file)

        collection = client.get_or_create_collection(
            name=pdf_name, embedding_function=openai_ef
        )

        if collection.count() == 0:
            logging.info(f"Creating collection for {pdf_name}")
            # Read and process the new PDF
            pdf_text = extract_text_from_pdf(pdf_file)
            text_chunks = tokenize_text(pdf_text)

            ids = [chunk["chunk_id"] for chunk in text_chunks]
            documents = [chunk["text"] for chunk in text_chunks]
            metadatas = [
                {"chunk_id": chunk["chunk_id"], "page_number": chunk["page_number"]}
                for chunk in text_chunks
            ]
            collection.add(documents=documents, metadatas=metadatas, ids=ids)
        else:
            logging.info(f"Using cached collection for {pdf_name}")
        # Process the questions
        question_list = [q.strip() for q in questions.strip().split("\n") if q.strip()]
        answers = {}

        for question in question_list:
            # Perform similarity search in ChromaDB
            results = collection.query(
                query_texts=[question],
                n_results=3,  # Retrieve top 3 most similar chunks
            )

            if results and results["documents"]:
                # Combine top chunks into context
                top_chunks = results["documents"][0]
                top_metadata = results["metadatas"][0]
                context = "\n\n".join(top_chunks)

                # Create the prompt
                prompt = f"""
                    You are an AI assistant that answers questions based solely on the provided context.
                    If the answer is not in the context, reply "Data Not Available".

                    Context:
                    \"\"\"
                    {context}
                    \"\"\"

                    Question:
                    {question}

                    Answer:"""

                # Get the answer from OpenAI
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                )

                answer = response.choices[0].message.content.strip()
                if answer and answer != "Data Not Available":
                    answers[question] = answer
                else:
                    answers[question] = "Data Not Available"
            else:
                answers[question] = "Data Not Available"

        return json.dumps(answers, indent=4)

    except Exception as e:
        return f"An error occurred: {str(e)}"


# Initialize OpenAI embedding function
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai.api_key, model_name="text-embedding-ada-002"
)

# Initialize ChromaDB client with persistent storage
client = chromadb.PersistentClient(path="./chroma_db")

# Gradio Interface
interface = gr.Interface(
    fn=answer_questions,
    inputs=[
        gr.File(label="Upload PDF", file_types=[".pdf"]),
        gr.Textbox(
            lines=5, placeholder="Enter questions (one per line)", label="Questions"
        ),
    ],
    outputs="text",
    title="PDF Question Answering Agent",
    description="Upload a PDF and enter your questions to receive answers based on the document's content.",
    allow_flagging="never",
)

if __name__ == "__main__":
    interface.launch()
