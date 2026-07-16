import os
from pathlib import Path
from typing import List, Dict, Any
from config import settings
from ingestion.doc_parser import extract_text


try:
    import boto3
except ImportError:
    boto3 = None




class DocumentLoader:
    """Loads documents from AWS S3 Knowledge Base bucket and local sample/uploaded directory."""


    def __init__(self):
        self.sample_dir = Path(settings.SAMPLE_DOCS_DIR)


    def load_from_s3(self) -> List[Dict[str, Any]]:
        """Download and read documents from AWS S3 bucket if configured."""
        documents = []
        if not settings.has_aws_credentials or not boto3:
            return documents


        try:
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_DEFAULT_REGION,
            )
            response = s3_client.list_objects_v2(Bucket=settings.AWS_S3_BUCKET_NAME)
            if "Contents" not in response:
                return documents


            for item in response["Contents"]:
                key = item["Key"]
                if key.endswith((".md", ".txt", ".json", ".pdf", ".docx")):
                    obj = s3_client.get_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=key)
                    # For S3 files, if it's text we read directly
                    content = obj["Body"].read()
                    try:
                        text_content = content.decode("utf-8", errors="ignore")
                    except Exception:
                        text_content = "Binary file downloaded from S3."
                    documents.append({
                        "content": text_content,
                        "metadata": {
                            "source": f"s3://{settings.AWS_S3_BUCKET_NAME}/{key}",
                            "filename": key,
                            "origin": "aws_s3"
                        }
                    })
        except Exception as e:
            print(f"[WARN] Could not load from S3 ({e}). Using local sample documents fallback.")
        return documents


    def load_local_samples(self) -> List[Dict[str, Any]]:
        """Load enterprise knowledge base documents (PDF, DOCX, MD, TXT) from local storage."""
        documents = []
        if not self.sample_dir.exists():
            return documents


        supported_exts = (".md", ".txt", ".pdf", ".docx")
        for file_path in self.sample_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_exts:
                try:
                    content = extract_text(file_path)
                    if content and content.strip():
                        documents.append({
                            "content": content,
                            "metadata": {
                                "source": str(file_path.name),
                                "filename": file_path.name,
                                "origin": "local_knowledge_base"
                            }
                        })
                except Exception as e:
                    print(f"[WARN] Error extracting {file_path}: {e}")
        return documents


    def load_all_documents(self) -> List[Dict[str, Any]]:
        """Load documents from both AWS S3 (if configured) and local samples."""
        s3_docs = self.load_from_s3()
        local_docs = self.load_local_samples()


        # Combine, avoiding duplicates by filename if already loaded from S3
        s3_filenames = {doc["metadata"]["filename"] for doc in s3_docs}
        combined = s3_docs + [d for d in local_docs if d["metadata"]["filename"] not in s3_filenames]
        return combined
