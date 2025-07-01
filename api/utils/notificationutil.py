from sqlmodel import Session, select, insert, literal
from typing import List
from settings import settings

from models.user import User
from models.notification import Notification
from models.application_setting import ApplicationSetting
from constants import ApplicationSettings

def notify_role(
    db: Session,
    triggered_by: int,
    roles: List[str],
    title: str,
    body: str
):
    notification_setting = db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == ApplicationSettings.NOTIFICATION_SETTING)
    ).first()
    if not notification_setting:
        raise Exception('Notification settings missing, perhaps you did not run initial migration or has been deleted')
    
    notification_enabled = notification_setting.value
    if notification_enabled != '1':
        return

    subquery = select(User.id).where(User.role.in_(roles))
    statement = (
        insert(Notification)
        .from_select(
            [
                Notification.user_id,
                Notification.triggered_by,
                Notification.title,
                Notification.body,
            ],
            select(
                subquery.c.id,
                triggered_by,
                literal(title),
                literal(body),
            )
        )
    )
    db.exec(statement)
    db.commit()

def notify_user(
    db: Session,
    triggered_by: int,
    user_id: int,
    title: str,
    body: str
):
    notification_setting = db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == ApplicationSettings.NOTIFICATION_SETTING)
    ).first()
    if not notification_setting:
        raise Exception('Notification settings missing, perhaps you did not run initial migration or has been deleted')
    
    notification_enabled = notification_setting.value
    if notification_enabled != '1':
        return
    
    notification = Notification(
        user_id=user_id,
        triggered_by=triggered_by,
        title=title,
        body=body
    )
    db.add(notification)
    db.commit()
