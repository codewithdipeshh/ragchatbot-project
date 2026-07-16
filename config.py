import os
from pathlib import Path
from dotenv import load_dotenv


# Load .env file if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")




class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")


    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_DEFAULT_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    AWS_S3_BUCKET_NAME: str = os.getenv("AWS_S3_BUCKET_NAME", "enterprise-knowledge-base-bucket")


    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    VECTOR_DB_DIR: str = os.getenv("VECTOR_DB_DIR", "./chroma_db")
    SAMPLE_DOCS_DIR: str = os.getenv("SAMPLE_DOCS_DIR", "./sample_docs")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")


    @property
    def has_groq_key(self) -> bool:
        key = self.GROQ_API_KEY.strip()
        return bool(key and key != "gsk_placeholder_enter_your_groq_api_key_here" and key != "gsk_y0urPr1vateGr0qKeyG0esHereUnst0ppable")


    @property
    def has_aws_credentials(self) -> bool:
        return bool(self.AWS_ACCESS_KEY_ID.strip() and self.AWS_SECRET_ACCESS_KEY.strip() and self.AWS_S3_BUCKET_NAME.strip())




settings = Settings()
