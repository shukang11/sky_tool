import time
import requests
from app import celery
from celery import Task
from app.command.email import Mail, Message
from app.command.rss import parser_feed

class CallBackTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        print(str(args))
        print(str(kwargs))
        url = None
        payload = {}
        if 'callback' in kwargs:
            url = kwargs['callback']
        payload['status'] = 'SUCCESS'
        payload['result'] = retval
        if url:
            requests.post(url, data=payload)
        return super(CallBackTask, self).on_success(retval, task_id, args, kwargs)
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        return super(CallBackTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@celery.task(base=CallBackTask)
def add(x: int, y: int, *args, **kwargs):
    time.sleep(5)
    result = x + y
    return result

@celery.task
def async_email_to(subject: str, body: str, recipients: list):
    user = "sunshukang30@163.com"
    password = "a12345678" # 授权码
    receivers = recipients
    sender = user
    try:
        mail = Mail("smtp.163.com", user, password, 465,  True, sender, 10)
        message = Message(subject=subject or "", recipients=receivers, body=body or "", sender=sender)
        mail.send(message)
        return 'done'
    except Exception as e:
        return e

@celery.task
def async_parser_feed(url: str):
    parser_feed(url)
