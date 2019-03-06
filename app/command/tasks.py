import time
from app.utils.ext import celery_app
from app.command.email import Mail, Message

@celery_app.task
def add(x, y):
    time.sleep(5)
    return x + y

@celery_app.task
def email(subject: str, body: str, recipients: list):
    user = "sunshukang30@163.com"
    password = "a12345678" # 授权码
    receivers = recipients
    sender = user
    mail = Mail("smtp.163.com", user, password, 465,  True, sender, 10)
    message = Message(subject=subject or "", recipients=receivers, body=body or "", sender=sender)
    mail.send(message)