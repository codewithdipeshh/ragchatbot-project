from typing import Dict, Any
from ingestion.s3_loader import DocumentLoader
from ingestion.chunker import DocumentChunker
from ingestion.embedder import LocalEmbedder




def run_cold_ingestion_pipeline() -> Dict[str, Any]:
    """Executes the complete Cold Ingestion Pipeline: S3/Local Load -> Chunk -> Embed -> Index."""
    loader = DocumentLoader()
    chunker = DocumentChunker(chunk_size=600, chunk_overlap=100)
    embedder = LocalEmbedder()


    # 1. Load documents
    documents = loader.load_all_documents()


    # 2. Segment into sliding overlapping chunks
    chunks = chunker.chunk_documents(documents)


    # 3. Embed & Index into local Chroma DB
    indexed_count = embedder.index_chunks(chunks)


    return {
        "status": "success",
        "documents_loaded": len(documents),
        "chunks_indexed": indexed_count,
        "total_index_count": embedder.get_count(),
        "sources": [doc["metadata"]["filename"] for doc in documents]
    }




if __name__ == "__main__":
    print("[INFO] Starting Enterprise RAG Cold Ingestion Pipeline...")
    results = run_cold_ingestion_pipeline()
    print(f"[SUCCESS] Cold Ingestion complete: {results}")
