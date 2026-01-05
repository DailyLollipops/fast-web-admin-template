from constants import ApplicationSettings
from sqlmodel import insert, literal, select

from api.database import get_sync_session
from api.database.models.application_setting import ApplicationSetting
from api.database.models.notification import Notification
from api.database.models.user import User


def notify_user(
    triggered_by: int,
    user_id: int,
    category: str,
    title: str,
    body: str
):
    with get_sync_session() as session:
        result = session.exec(
            select(ApplicationSetting)
            .where(ApplicationSetting.name == ApplicationSettings.NOTIFICATION_SETTING)
        )
        notification_setting = result.first()
        if not notification_setting:
            raise Exception('Notification settings missing, perhaps you did not run initial migration')
        
        notification_enabled = notification_setting.value
        if notification_enabled != '1':
            return
        
        notification = Notification(
            user_id=user_id,
            triggered_by=triggered_by,
            category=category,
            title=title,
            body=body
        ) # type: ignore
        session.add(notification)
        session.commit()


def notify_role(
    triggered_by: int,
    roles: list[str],
    category: str,
    title: str,
    body: str
):
    with get_sync_session() as session:
        result = session.exec(
            select(ApplicationSetting)
            .where(ApplicationSetting.name == ApplicationSettings.NOTIFICATION_SETTING)
        )
        notification_setting = result.first()
        if not notification_setting:
            raise Exception('Notification settings missing, perhaps you did not run initial migration')
        
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
                    Notification.category,
                    Notification.title,
                    Notification.body,
                ], # type: ignore
                select(
                    subquery.c.id,
                    triggered_by,
                    literal(category),
                    literal(title),
                    literal(body),
                ) # type: ignore
            )
        )
        session.exec(statement) # type: ignore
        session.commit()
