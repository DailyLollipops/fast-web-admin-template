from constants import ApplicationSettings
from models.application_setting import ApplicationSetting
from models.notification import Notification
from models.user import User
from sqlmodel import Session, insert, literal, select


def notify_role(
    db: Session,
    triggered_by: int,
    roles: list[str],
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

    subquery = select(User.id).where(User.role.in_(roles)) # type: ignore
    statement = (
        insert(Notification)
        .from_select(
            [
                Notification.user_id,
                Notification.triggered_by,
                Notification.title,
                Notification.body,
            ], # type: ignore
            select(
                subquery.c.id,
                triggered_by,
                literal(title),
                literal(body),
            )
        )
    )
    db.exec(statement) # type: ignore
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
