from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # GitHub配置
    github_token: str
    
    # MongoDB配置
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "talentrank"
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # 缓存配置
    cache_ttl: int = 3600  # 缓存有效期（秒）
    
    class Config:
        env_file = ".env"

settings = Settings() 