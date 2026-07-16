from typing import List, Dict, Any


try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
class DocumentChunker:
    """Segments documents into overlapping text chunks for semantic indexing."""


    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]
        )
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        for doc in documents:
            content = doc["content"]
            metadata = doc["metadata"]
            split_texts = self.splitter.split_text(content)


            for idx, text in enumerate(split_texts):
                if not text.strip():
                    continue
                chunk_meta = dict(metadata)
                chunk_meta["chunk_index"] = idx
                chunk_id = f"{metadata.get('filename', 'doc')}_chunk_{idx}"


                chunks.append({
                    "id": chunk_id,
                    "text": text.strip(),
                    "metadata": chunk_meta
                })
        return chunks





