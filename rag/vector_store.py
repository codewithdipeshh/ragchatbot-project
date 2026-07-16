from typing import List, Dict, Any
from ingestion.embedder import LocalEmbedder




class VectorStoreRetriever:
    """Queries Chroma DB for top-K semantically relevant document chunks."""


    def __init__(self, collection_name: str = "enterprise_knowledge_base"):
        self.embedder = LocalEmbedder(collection_name=collection_name)


    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        collection = self.embedder.collection
        if collection.count() == 0:
            return []


        # Perform semantic top-k query
        num_results = min(top_k, collection.count())
        results = collection.query(
            query_texts=[query],
            n_results=num_results
        )


        retrieved_contexts = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0] if "distances" in results else [0.0] * len(documents)


        for i, doc_text in enumerate(documents):
            meta = metadatas[i] if i < len(metadatas) else {}
            dist = distances[i] if i < len(distances) else 0.0
            # Convert cosine distance to similarity percentage estimate
            similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))


            retrieved_contexts.append({
                "text": doc_text,
                "source": meta.get("filename", meta.get("source", "Knowledge Base")),
                "chunk_index": meta.get("chunk_index", i),
                "similarity": round(similarity * 100, 1)
            })


        return retrieved_contexts


    def list_indexed_sources(self) -> List[Dict[str, Any]]:
        collection = self.embedder.collection
        count = collection.count()
        if count == 0:
            return []
        data = collection.get(include=["metadatas"])
        metas = data.get("metadatas", [])
        unique_sources = {}
        for m in metas:
            if not m:
                continue
            fn = m.get("filename", m.get("source", "Unknown"))
            unique_sources[fn] = unique_sources.get(fn, 0) + 1


        return [
            {"filename": fn, "chunks_count": cnt}
            for fn, cnt in unique_sources.items()
        ]


