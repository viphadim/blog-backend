
from pydantic_settings import BaseSettings  # 
class Settings(BaseSettings):
    APP_NAME: str = "Blogs API"
    DEBUG: bool = True

    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str | None = None
    DATABASE_NAME: str | None = None
    DATABASE_PORT: str = "5433"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"
settings = Settings()