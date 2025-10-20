"""
RAG Chatbot Configuration Module
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # SageMaker Configuration
    sagemaker_endpoint_name: str = Field(default="llama3-endpoint", env="SAGEMAKER_ENDPOINT_NAME")
    sagemaker_role_arn: Optional[str] = Field(default=None, env="SAGEMAKER_ROLE_ARN")
    
    # Vector Database Configuration
    vector_db_type: str = Field(default="chroma", env="VECTOR_DB_TYPE")
    pinecone_api_key: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    pinecone_index_name: str = Field(default="rag-chatbot-index", env="PINECONE_INDEX_NAME")
    
    # Embedding Model Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", 
        env="EMBEDDING_MODEL"
    )
    chunk_size: int = Field(default=512, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, env="CHUNK_OVERLAP")
    
    # LLM Configuration
    llm_model_name: str = Field(
        default="meta-llama/Llama-2-7b-chat-hf", 
        env="LLM_MODEL_NAME"
    )
    max_tokens: int = Field(default=2048, env="MAX_TOKENS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    
    # Ollama Configuration
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model_name: str = Field(default="llama3.1:8b-instruct", env="OLLAMA_MODEL_NAME")
    ollama_timeout: int = Field(default=300, env="OLLAMA_TIMEOUT")
    
    # Application Configuration
    app_port: int = Field(default=8000, env="APP_PORT")
    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Document Processing
    upload_dir: str = Field(default="./documents", env="UPLOAD_DIR")
    processed_dir: str = Field(default="./processed_docs", env="PROCESSED_DIR")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
