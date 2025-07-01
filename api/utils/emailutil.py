from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Template
from sqlmodel import Session, select

from models.application_setting import ApplicationSetting
from constants import ApplicationSettings
import os

async def get_smtp_config(db: Session):
    smtp_server = db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == ApplicationSettings.SMTP_SERVER)
    ).first().value
    smtp_port = db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == ApplicationSettings.SMTP_PORT)
    ).first().value
    smtp_username = db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == ApplicationSettings.SMTP_USERNAME)
    ).first().value
    smtp_password = db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == ApplicationSettings.SMTP_PASSWORD)
    ).first().value
    config = ConnectionConfig(
        MAIL_USERNAME=smtp_username,
        MAIL_PASSWORD=smtp_password,
        MAIL_FROM=smtp_username,
        MAIL_PORT=smtp_port,
        MAIL_SERVER=smtp_server,
        MAIL_STARTTLS = False,
        MAIL_SSL_TLS = True,
        USE_CREDENTIALS = True,
        VALIDATE_CERTS = True
    )
    return config


async def send_email(db: Session, template: str, data: dict, subject: str, recipients: list[str]):
    with open(template, 'r') as file:
        email_template = Template(file.read())
    rendered_html = email_template.render(**data)
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=rendered_html,
        subtype="html"
    )
    smtp_config = await get_smtp_config(db)

    fm = FastMail(smtp_config)
    await fm.send_message(message)
