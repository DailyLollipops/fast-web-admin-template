from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str 
    MYSQL_DATABASE: str 
    DATABASE_URL: str
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    SECRET_KEY: str
    REDIS_NOTIFICATION_CHANNEL: str = 'notifications'
    REDIS_EMAIL_CHANNEL: str = 'emails'
    PROFILE_DIRECTORY: str = 'static/profiles'

settings = Settings()
