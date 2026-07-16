import os
import time
import uuid
from pathlib import Path
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


from config import settings
from rag.graph import RAGWorkflow
from rag.vector_store import VectorStoreRetriever
from ingestion.pipeline import run_cold_ingestion_pipeline
from ingestion.doc_parser import extract_text
from ingestion.chunker import DocumentChunker
from ingestion.embedder import LocalEmbedder


app = FastAPI(
    title="Enterprise RAG-Driven Chatbot Architecture API",
    description="Orchestrations & Processing Layer with LangGraph, Chroma DB, and Groq Llama 3.3",
    version="1.1.0",
)


# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Pydantic Schemas
class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's prompt query string")




class SourceCitation(BaseModel):
    text: str
    source: str
    chunk_index: int
    similarity: float




class ChatResponse(BaseModel):
    request_id: str
    answer: str
    sources: List[SourceCitation]
    latency_ms: int
    model_used: str
    groundedness_score: float




class HealthResponse(BaseModel):
    status: str
    chroma_db_indexed_chunks: int
    groq_configured: bool
    aws_s3_configured: bool
    groq_model: str




# Instantiate workflow lazy singleton
_workflow_instance: Optional[RAGWorkflow] = None




def get_workflow() -> RAGWorkflow:
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = RAGWorkflow()
    return _workflow_instance




@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Execute LangGraph state machine cycle for a user query."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query prompt cannot be empty.")


    request_id = str(uuid.uuid4())
    workflow = get_workflow()


    try:
        result = workflow.execute(request.query)


        sources = [
            SourceCitation(
                text=src.get("text", ""),
                source=src.get("source", "Knowledge Base"),
                chunk_index=src.get("chunk_index", 0),
                similarity=src.get("similarity", 0.0),
            )
            for src in result.get("sources", [])
        ]


        return ChatResponse(
            request_id=request_id,
            answer=result.get("response", "No response generated."),
            sources=sources,
            latency_ms=result.get("latency_ms", 0),
            model_used=result.get("model_used", "Local RAG Engine"),
            groundedness_score=result.get("groundedness_score", 0.0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference pipeline failure: {str(e)}")




@app.post("/api/upload")
async def upload_document_endpoint(file: UploadFile = File(...)):
    """Upload a PDF, DOCX, TXT, or MD file, extract its text, and index it into Chroma DB immediately."""
    try:
        sample_dir = Path(settings.SAMPLE_DOCS_DIR)
        sample_dir.mkdir(parents=True, exist_ok=True)


        file_path = sample_dir / file.filename
        content_bytes = await file.read()
        file_path.write_bytes(content_bytes)


        # Extract text using doc_parser
        text_content = extract_text(file_path)
        if not text_content or not text_content.strip():
            raise HTTPException(status_code=400, detail=f"Could not extract text from {file.filename}")


        # Chunk and index immediately
        chunker = DocumentChunker(chunk_size=600, chunk_overlap=100)
        embedder = LocalEmbedder()


        doc = {
            "content": text_content,
            "metadata": {
                "source": file.filename,
                "filename": file.filename,
                "origin": "user_uploaded_document"
            }
        }
        chunks = chunker.chunk_documents([doc])
        indexed_count = embedder.index_chunks(chunks)


        return {
            "status": "success",
            "filename": file.filename,
            "chunks_indexed": indexed_count,
            "total_index_count": embedder.get_count(),
            "message": f"Successfully extracted and indexed {file.filename} ({indexed_count} chunks)."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload & extraction failed: {str(e)}")




@app.post("/api/ingest")
async def ingest_endpoint():
    """Trigger the Cold Ingestion Pipeline to sync AWS S3 and local sample documents into Chroma DB."""
    try:
        results = run_cold_ingestion_pipeline()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cold ingestion failure: {str(e)}")




@app.get("/api/health", response_model=HealthResponse)
async def health_endpoint():
    """System health check and infrastructure readiness report."""
    try:
        retriever = VectorStoreRetriever()
        chunk_count = retriever.embedder.get_count()
    except Exception:
        chunk_count = 0

    return HealthResponse(
        status="operational",
        chroma_db_indexed_chunks=chunk_count,
        groq_configured=settings.has_groq_key,
        aws_s3_configured=settings.has_aws_credentials,
        groq_model=settings.GROQ_MODEL_NAME,
    )

@app.get("/api/sources")
async def sources_endpoint():
    """Return all unique knowledge documents currently indexed in Chroma DB."""
    try:
        retriever = VectorStoreRetriever()
        sources = retriever.list_indexed_sources()
        return {"indexed_sources": sources, "total_documents": len(sources)}
    except Exception as e:
        return {"indexed_sources": [], "error": str(e)}
    
@app.get("/")
async def root():
    return {
        "service": "Enterprise RAG-Driven Chatbot Architecture Backend",
        "documentation": "/docs",
        "endpoints": ["/api/chat", "/api/upload", "/api/ingest", "/api/health", "/api/sources"],
    }
