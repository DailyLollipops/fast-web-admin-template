from redis import Redis
from rq import Queue
from settings import settings


def get_notification_queue():
    with Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0
    ) as redis:
        queue = Queue('notification', connection=redis)
        yield queue


def get_email_queue():
    with Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0
    ) as redis:
        queue = Queue('email', connection=redis)
        yield queue
