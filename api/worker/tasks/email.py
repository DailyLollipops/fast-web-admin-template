import asyncio

from constants import ApplicationSettings
from database import get_sync_session
from database.models.application_setting import ApplicationSetting
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Template
from sqlmodel import Session, select


def get_smtp_config(db: Session):
    def get_setting_value(name: str) -> str:
        q = (
            select(ApplicationSetting)
            .where(ApplicationSetting.name == name)
        )
        if setting := db.exec(q).first():
            return setting.value
        return ""

    smtp_server = get_setting_value(ApplicationSettings.SMTP_SERVER)
    smtp_port = get_setting_value(ApplicationSettings.SMTP_PORT)
    smtp_username = get_setting_value(ApplicationSettings.SMTP_USERNAME)
    smtp_password = get_setting_value(ApplicationSettings.SMTP_PASSWORD)
    config = ConnectionConfig(
        MAIL_USERNAME=smtp_username,
        MAIL_PASSWORD=smtp_password,
        MAIL_FROM=smtp_username,
        MAIL_PORT=int(smtp_port),
        MAIL_SERVER=smtp_server,
        MAIL_STARTTLS = False,
        MAIL_SSL_TLS = True,
        USE_CREDENTIALS = True,
        VALIDATE_CERTS = True
    )
    return config


def send_email(template: str, data: dict, subject: str, recipients: list[str]):
    with get_sync_session() as session:
        with open(template) as file:
            email_template = Template(file.read())
        rendered_html = email_template.render(**data)
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=rendered_html,
            subtype=MessageType.html
        )
        smtp_config = get_smtp_config(session)

        fm = FastMail(smtp_config)
        asyncio.run(fm.send_message(message))
