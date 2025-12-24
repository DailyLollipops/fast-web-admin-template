from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    SECRET_KEY: str = 'change-me'
    ACCESS_TOKEN_EX: int = 3600 # 1 hour
    EMAIL_TOKEN_EX: int = 900 # 15 minutes

    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str

    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_NOTIFICATION_CHANNEL: str = 'notifications'
    REDIS_EMAIL_CHANNEL: str = 'emails'

    PROFILE_DIRECTORY: str = 'static/profiles'

settings = Settings() # type: ignore
