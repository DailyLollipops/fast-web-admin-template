from constants import ApplicationSettings
from database.models.application_setting import ApplicationSetting
from database.models.notification import Notification
from database.models.user import User
from sqlmodel import insert, literal, select
from sqlmodel.ext.asyncio.session import AsyncSession


async def notify_role(
    db: AsyncSession,
    triggered_by: int,
    roles: list[str],
    title: str,
    body: str
):
    result = await db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == ApplicationSettings.NOTIFICATION_SETTING)
    )
    notification_setting = result.first()
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
    await db.exec(statement) # type: ignore
    await db.commit()

async def notify_user(
    db: AsyncSession,
    triggered_by: int,
    user_id: int,
    title: str,
    body: str
):
    result = await db.exec(
        select(ApplicationSetting)
        .where(ApplicationSetting.name == ApplicationSettings.NOTIFICATION_SETTING)
    )
    notification_setting = result.first()
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
    await db.commit()
