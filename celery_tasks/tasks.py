import time
import requests
from celery_tasks import celery
from celery import Task
from celery_tasks.email import Mail, Message
from celery_tasks.rss import parser_feed
import records

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

@celery.task(bind=True, ignore_result=True, default_retry_delay=300, max_retries=3)
def async_email_to(subject: str, body: str, recipients: list):
    user = "sunshukang30@163.com"
    password = "a12345678"  # 授权码
    receivers = recipients
    sender = user
    mail = Mail("smtp.163.com", user, password, 465,  True, sender, 10)
    message = Message(subject=subject or "",
                        recipients=receivers, body=body or "", sender=sender)
    mail.send(message)

@celery.task(bind=True, default_retry_delay=300, max_retries=3)
def async_parser_feed(url: str):
    result = parser_feed(url)
    version = result['version']
    title = result['title']
    link = result['link']
    subtitle = result['subtitle']
    items = result['items']
    print(items)
    return result


@celery.task(base=CallBackTask)  # 指定回调
def add(x: int, y: int, *args, **kwargs):
    time.sleep(5)
    result = x + y
    return result


@celery.task(bind=True)  # 将上下文环境绑定到当前
def mul(self, x: int, y: int, *args, **kwargs):
    print('Executing task id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r} callbacks: {0.callbacks!r}'.format(
        self.request))
    time.sleep(5)
    result = x + y
    return result
