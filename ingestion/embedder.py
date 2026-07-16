import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from config import settings




class LocalEmbedder:
    """Embeds text chunks and indexes them into Chroma DB persistent collection."""


    def __init__(self, collection_name: str = "enterprise_knowledge_base"):
        os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_DIR)


        # Try initializing HuggingFace embedding function or fallback to Chroma default sentence transformer
        self.embedding_fn = self._get_embedding_function()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )


    def _get_embedding_function(self):
        try:
            from chromadb.utils import embedding_functions
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=settings.EMBEDDING_MODEL_NAME
            )
        except Exception as e:
            print(f"[INFO] Using ChromaDB default embedding function ({e})")
            from chromadb.utils import embedding_functions
            return embedding_functions.DefaultEmbeddingFunction()


    def index_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Add or update chunk embeddings in Chroma DB."""
        if not chunks:
            return 0


        ids = [chunk["id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "source": str(chunk["metadata"].get("source", "Unknown")),
                "filename": str(chunk["metadata"].get("filename", "Unknown")),
                "origin": str(chunk["metadata"].get("origin", "local")),
                "chunk_index": int(chunk["metadata"].get("chunk_index", 0)),
            }
            for chunk in chunks
        ]


        # Upsert into ChromaDB collection
        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        return len(ids)


    def get_count(self) -> int:
        return self.collection.count()
