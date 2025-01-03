
# PDF Question Answering Agent

This application allows users to upload a PDF document and input a list of questions. The AI agent leverages Anthropic's GPT models to extract answers from the content of the PDF. It uses ChromaDB to store embeddings for efficient semantic search and relies on unique `pdf_id` identifiers to manage data for PDFs that are uploaded.

## Features

- **PDF Parsing**: Extracts text from PDFs and splits it into tokenized chunks for efficient processing.
- **Embeddings Storage**: Uses ChromaDB for storing embeddings and performing semantic search on Sentence Transformers embeddings.
- **Question Answering**: Utilizes claude's GPT models to generate answers based on the document's content that's most relevant to the question.
- **Unique Identification**: Assigns a unique `pdf_id` to each uploaded PDF for data management.
- **Persistent Storage**: Ensures that embeddings persist across application restarts.
- **Scalable**: Simplified design without a database, enabling easy scaling and deployment.

---

## Getting Started

### Prerequisites

1. **Python 3.10**
2. **Docker (optional for containerized deployment)**
3. **Anthropic API Key**

### Installation

#### Clone the Repository

```bash
git clone https://github.com/divmakkar/pdf-question-answering-agent.git
cd pdf-question-answering-agent
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Running the Application

#### 1. Without Docker

1. **Set the Anthropic API Key**

   Export your Anthropic API key as an environment variable:

   ```bash
   export ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

2. **Run the Application**

   ```bash
   python -m app.main
   ```

3. **Access the API**

   Open a browser and navigate to `http://localhost:8000/docs` to view and interact with the API documentation.

#### 2. With Docker

1. **Build the Docker Image**

   ```bash
   docker build -t pdf-qa-app .
   ```

2. **Run the Docker Container**

   ```bash
   docker run -e ANTHROPIC_API_KEY=your_claude_api_key -p 8000:8000 pdf-qa-app
   ```

3. **Access the API**

   Open a browser and navigate to `http://localhost:8000/docs`.

---

## API Endpoints

### **Upload a PDF**

- **Endpoint**: `POST /upload_pdf/`
- **Description**: Uploads a PDF and processes it for question answering.
- **Request**: Form-data with a file field containing the PDF.
- **Response**:
  ```json
  {
    "message": "PDF processed and embeddings updated.",
    "pdf_id": "unique-pdf-id"
  }
  ```

### **Ask Questions**

- **Endpoint**: `POST /ask_questions/`
- **Description**: Answers questions based on the content of a previously uploaded PDF.
- **Request**:
  ```json
  {
    "questions": ["What is the main topic?", "Who are the authors?"],
    "pdf_id": "unique-pdf-id"
  }
  ```
- **Response**:
  ```json
  {
    "What is the main topic?": "The main topic is ...",
    "Who are the authors?": "The authors are ..."
  }
  ```

---

## Project Structure

```
pdf-question-answering-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                # Entry point for the FastAPI application
│   ├── routers/
│   │   ├── __init__.py
│   │   └── api.py             # API endpoints for PDF upload and question answering
│   ├── models/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py   # Handles PDF text extraction and tokenization
│   │   ├── embeddings_manager.py  # Manages embeddings with ChromaDB
│   │   └── question_answering.py  # Handles interaction with Anthropic GPT models
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   └── logger.py          # Logging setup
├── requirements.txt           # List of Python dependencies
├── Dockerfile                 # Dockerfile for containerized deployment
├── README.md                  # Project documentation
└── .gitignore                 # Files and directories to ignore in version control
```



## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact

For questions or support, feel free to reach out to:

- **Email**: divu.mkr@gmail.com
- **GitHub**: [divmakkar](https://github.com/divmakkar)

