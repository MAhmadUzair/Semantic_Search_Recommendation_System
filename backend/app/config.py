from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl
import os


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    EMBEDDING_MODEL: str = Field("text-embedding-3-small", env="EMBEDDING_MODEL")

    # Qdrant (cloud)
    QDRANT_API_KEY: str = Field(default="", env="QDRANT_API_KEY")
    QDRANT_URL: str = Field(default="", env="QDRANT_URL")
    QDRANT_COLLECTION: str = Field("semantic_spots", env="QDRANT_COLLECTION")

    # Backend
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")

    class Config:
        env_file = ".env"  # Look for .env in current working directory
        env_file_encoding = "utf-8"

    def validate_required_fields(self):
        """Validate that required fields are set."""
        required_fields = {
            'OPENAI_API_KEY': self.OPENAI_API_KEY,
            'QDRANT_API_KEY': self.QDRANT_API_KEY,
            'QDRANT_URL': self.QDRANT_URL
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            raise ValueError(f"Missing required environment variables: {missing_fields}")


settings = Settings()
