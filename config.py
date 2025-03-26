from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Intellisearch"
    openai_api_key: str
    DATABASE_URL: str
    pinecone_api_key: str
    pinecone_index_name: str
    pinecone_dimension: int
    pinecone_metric: str
    pinecone_cloud: str
    pinecone_region: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create a settings instance that can be imported and used across the application
settings = Settings()