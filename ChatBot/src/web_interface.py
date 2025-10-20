"""
Web Interface for RAG Chatbot using FastAPI
Provides REST API endpoints and basic web interface
"""
import logging
import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from .config import settings
from .document_processor import DocumentProcessor
from .vector_database import VectorDatabase
from .llm_integration import RAGPipeline, SageMakerLLM, LocalLLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation Chatbot with document upload and querying capabilities",
    version="1.0.0"
)

# Pydantic models for API
class QueryRequest(BaseModel):
    question: str
    num_docs: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    num_sources: int

class DocumentUploadResponse(BaseModel):
    message: str
    files_processed: int
    chunks_created: int

# Global components
processor = None
vector_db = None
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global processor, vector_db, rag_pipeline
    
    try:
        logger.info("Initializing RAG Chatbot components...")
        
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Initialize vector database
        vector_db = VectorDatabase(settings.vector_db_type)
        
        # Try to load existing vector store
        try:
            vector_db.load()
            logger.info("Loaded existing vector store")
        except:
            logger.info("No existing vector store found, will create new one")
        
        # Initialize LLM (try SageMaker first, fallback to Local)
        try:
            llm = SageMakerLLM()
            logger.info("Using SageMaker LLM")
        except:
            llm = LocalLLM()
            logger.info("Using Local LLM")
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(vector_db, llm)
        
        logger.info("RAG Chatbot initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG Chatbot: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main chatbot interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RAG Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: auto; padding: 10px; margin: 20px 0; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background-color: #e3f2fd; text-align: right; }
            .bot-message { background-color: #f5f5f5; }
            .input-container { display: flex; gap: 10px; }
            .input-container input { flex: 1; padding: 10px; }
            .input-container button { padding: 10px 20px; }
            .upload-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>RAG Chatbot</h1>
        
        <div class="upload-section">
            <h3>Upload Documents</h3>
            <form id="uploadForm" enctype="multipart/form-data">
                <input type="file" id="fileInput" multiple accept=".pdf,.docx,.txt,.html">
                <button type="submit">Upload</button>
            </form>
            <div id="uploadStatus"></div>
        </div>
        
        <div class="chat-container" id="chatContainer"></div>
        
        <div class="input-container">
            <input type="text" id="questionInput" placeholder="Ask a question..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <script>
            async function sendMessage() {
                const input = document.getElementById('questionInput');
                const question = input.value.trim();
                if (!question) return;
                
                const chatContainer = document.getElementById('chatContainer');
                
                // Add user message
                chatContainer.innerHTML += `<div class="message user-message"><strong>You:</strong> ${question}</div>`;
                input.value = '';
                
                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question: question })
                    });
                    
                    const data = await response.json();
                    
                    // Add bot message
                    chatContainer.innerHTML += `<div class="message bot-message">
                        <strong>Bot:</strong> ${data.answer}<br>
                        <small>Confidence: ${(data.confidence * 100).toFixed(1)}% | Sources: ${data.num_sources}</small>
                    </div>`;
                    
                } catch (error) {
                    chatContainer.innerHTML += `<div class="message bot-message"><strong>Bot:</strong> Error: ${error.message}</div>`;
                }
                
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const fileInput = document.getElementById('fileInput');
                const files = fileInput.files;
                
                if (files.length === 0) return;
                
                const formData = new FormData();
                for (let file of files) {
                    formData.append('files', file);
                }
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    document.getElementById('uploadStatus').innerHTML = `<p style="color: green;">${data.message}</p>`;
                    fileInput.value = '';
                    
                } catch (error) {
                    document.getElementById('uploadStatus').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Save uploaded files
        saved_files = []
        for file in files:
            file_path = os.path.join(settings.upload_dir, file.filename)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            saved_files.append(file_path)
        
        # Process documents
        documents = processor.process_documents(saved_files)
        
        # Add to vector database
        vector_db.add_documents(documents)
        
        # Save vector store
        vector_db.save()
        
        return DocumentUploadResponse(
            message=f"Successfully processed {len(files)} files",
            files_processed=len(files),
            chunks_created=len(documents)
        )
        
    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_chatbot(request: QueryRequest):
    """Query the RAG chatbot"""
    try:
        if not rag_pipeline:
            raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
        
        # Process query through RAG pipeline
        response = rag_pipeline.query(request.question, request.num_docs)
        
        return QueryResponse(**response)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "RAG Chatbot is running"}

@app.get("/stats")
async def get_stats():
    """Get chatbot statistics"""
    try:
        # This would need to be implemented based on your vector store
        return {
            "vector_db_type": settings.vector_db_type,
            "embedding_model": settings.embedding_model,
            "llm_model": settings.llm_model_name,
            "status": "operational"
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    """Run the FastAPI application"""
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
