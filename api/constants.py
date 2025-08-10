from enum import Enum


class ApplicationSettings(str, Enum):
    NOTIFICATION_SETTING = 'notification'
    USER_VERIFICATION = 'user_verification'
    BASE_URL = 'base_url'
    SMTP_SERVER = 'smtp_server'
    SMTP_PORT = 'smtp_port'
    SMTP_USERNAME = 'smtp_username'
    SMTP_PASSWORD = 'smtp_password'

class VerificationMethod(str, Enum):
    NONE = 'none'
    EMAIL = 'email'
