from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    EMBEDDING_MODEL: str = Field("text-embedding-3-small", env="EMBEDDING_MODEL")

    # Qdrant (cloud)
    QDRANT_API_KEY: str = Field(..., env="QDRANT_API_KEY")
    QDRANT_URL: AnyUrl = Field(..., env="QDRANT_URL")
    QDRANT_COLLECTION: str = Field("semantic_spots", env="QDRANT_COLLECTION")

    # Backend
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
