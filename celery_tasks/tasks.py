import time
import requests
from celery_tasks import celery_app, db
from celery import Task
from celery_tasks.email import Mail, Message
from celery_tasks.monitor import exec_cmd
from celery_tasks.rss import parser_feed, parse_inner
from app.utils import get_unix_time_tuple

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

@celery.task(base=CallBackTask)  # 指定回调
def add(x: int, y: int, *args, **kwargs):
    time.sleep(5)
    result = x + y
    return result

@celery.task(ignore_result=True, default_retry_delay=300, max_retries=3)
def async_email_to(subject: str, body: str, recipients: list):
    """
    send email
    Args:
    subject: 邮件主题
    body: 邮件内容， 当前只支持字符
    recipients: 收件人
    Return: None
    """
    user = "sunshukang30@163.com"
    password = "a12345678"  # 授权码
    receivers = recipients
    sender = user
    mail = Mail("smtp.163.com", user, password, 465,  True, sender, 10)
    message = Message(subject=subject or "",
                        recipients=receivers, body=body or "", sender=sender)
    mail.send(message)

@celery.task(default_retry_delay=300, max_retries=3, ignore_result=True)
def async_parser_feed(url: str):
    """
    开始解析rss任务
    Args:
    url: rss地址
    Return: 字典，包含了解析的结果
    """
    result = parser_feed(url)
    parse_inner(url, result)
    return result

# deat mession

@celery.task(default_retry_delay=300, max_retries=3, ignore_result=True)
def report_local_ip():
    import time
    today = str(time.localtime(time.time()))
    ifconfig_result = str(exec_cmd("ifconfig -a"))
    async_email_to(today, ifconfig_result, ['804506054@qq.com'])

@celery.task(default_retry_delay=300, max_retries=3, ignore_result=True)
def parse_rsses():
    sql = """
    SELECT bao_rss.rss_link FROM bao_rss;
    """
    links = db.query(sql)
    for link in links:
        async_parser_feed(link['rss_link'])
    
