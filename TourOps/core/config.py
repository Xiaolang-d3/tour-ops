import yaml
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

_config = load_config()

class Settings:
    PROJECT_NAME: str = "TripSched"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DB_HOST: str = _config["database"]["host"]
    DB_PORT: int = _config["database"]["port"]
    DB_USER: str = _config["database"]["user"]
    DB_PASSWORD: str = _config["database"]["password"]
    DB_NAME: str = _config["database"]["name"]
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # JWT
    SECRET_KEY: str = _config["jwt"]["secret_key"]
    ALGORITHM: str = _config["jwt"]["algorithm"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = _config["jwt"]["expire_minutes"]
    
    # AI
    AI_API_KEY: str = _config.get("ai", {}).get("api_key", "")
    AI_MODEL: str = _config.get("ai", {}).get("model", "qwen-turbo")
    AI_BASE_URL: str = _config.get("ai", {}).get("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")

settings = Settings()
