from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Settings
    project_name: str = "BLE Beacon Presence Tracking API"
    api_v1_str: str = "/v1"
    debug: bool = False
    
    # Database
    database_url: str
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # FCM Configuration (DISABLED - endpoints removed)
    # fcm_server_key: Optional[str] = None
    # fcm_sender_id: Optional[str] = None
    # fcm_service_account_key_path: Optional[str] = None
    # fcm_project_id: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
