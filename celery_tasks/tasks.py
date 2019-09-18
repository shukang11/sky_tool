from typing import List, Optional, Dict, Tuple
import time
import logging
import requests
import pymysql
import os
from celery_tasks import celery_app, db
from celery import Task
from celery_tasks.email import Mail, Message
from celery_tasks.monitor import exec_cmd
from celery_tasks.rss import parser_feed, parse_inner
from app.utils import get_unix_time_tuple
from app.models import TaskModel

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


@celery_app.task(base=CallBackTask)  # 指定回调
def add(x: int, y: int, *args, **kwargs):
    time.sleep(5)
    result = x + y
    return result


@celery_app.task(ignore_result=False, default_retry_delay=300, max_retries=3)
def async_email_to(subject: str,
                   body: str,
                   recipients: List[str],
                   attaches: Optional[List[str]],
                   extra_headers: Optional[Dict[str, str]]=None):
    """
    send email
    Args:
    subject: 邮件主题
    body: 邮件内容， 当前只支持字符
    recipients: 收件人
    Return: None
    """

    smtp_mail = os.environ.get('SMPT_MAIL_163', None)
    auth_code = os.environ.get('SMPT_MAIL_163_AUTH_CODE', None)
    need_ssl = True
    port: str = ""
    if need_ssl:
        port = os.environ.get('SMPT_MAIL_163_SSL_PORT', None)
    else:
        port = os.environ.get('SMPT_MAIL_163_NORMAL_PORT', None)
    password = auth_code  # 授权码
    receivers = recipients
    sender = smtp_mail
    mail = Mail("smtp.163.com",
                smtp_mail,
                password,
                port,
                need_ssl,
                sender,
                10)
    message = Message(subject=subject or "",
                      recipients=receivers,
                      body=body or "",
                      sender=sender,
                      attaches=attaches,
                      extra_headers=extra_headers)
    mail.send(message)


@celery_app.task(default_retry_delay=300, max_retries=3, ignore_result=True)
def async_parser_feed(url: str, user_id: int = None):
    """
    开始解析rss任务
    Args:
    url: rss地址
    Return: 字典，包含了解析的结果
    """
    taskid = None
    parse_result = False
    if hasattr(async_parser_feed.request, 'task'):
        r = async_parser_feed.request
        sql = """
        INSERT INTO bao_task_record(task_id, tast_name, user_id, argsrepr, kwargs, begin_at, is_succ) 
        VALUES ('{task_id}', '{tast_name}', '{user_id}', '{argsrepr}', '{kwargs}', '{begin_at}', '{is_succ}') 
        ON DUPLICATE KEY UPDATE begin_at='{begin_at}';
        """.format(task_id=r.id,
                   tast_name=r.task,
                   user_id=0,
                   argsrepr=pymysql.escape_string(
                       str(r.args)),
                   kwargs=pymysql.escape_string(
                       str(r.kwargs)),
                   begin_at=get_unix_time_tuple(),
                   is_succ=int(parse_result))
        db.query(sql)
    result = parser_feed(url)
    sql = """
    UPDATE bao_rss SET bao_rss.rss_subtitle = '{subtitle}', 
    bao_rss.rss_title = '{title}', 
    bao_rss.rss_version='{version}' 
    WHERE bao_rss.rss_link='{link}';
    """.format(
        title=result.get('title') if result else '',
        subtitle=result.get('subtitle') if result else '',
        version=result.get('version') if result else '',
        link=url
    )
    db.query(sql)
    if result:
        parse_result = parse_inner(url, result)

    if hasattr(async_parser_feed.request, 'task'):
        r = async_parser_feed.request
        sql = """
        UPDATE bao_task_record SET end_at='{end_at}', is_succ={is_succ} WHERE task_id='{task_id}'
        """.format(task_id=r.id, is_succ=int(parse_result), end_at=get_unix_time_tuple())
        db.query(sql)
    return result

# deat mession


@celery_app.task(default_retry_delay=300, max_retries=3, ignore_result=True)
def report_local_ip():
    import time
    today = str(time.localtime(time.time()))
    ifconfig_result = str(exec_cmd("ifconfig -a"))
    async_email_to(today, ifconfig_result, ['804506054@qq.com'])


@celery_app.task(default_retry_delay=300, max_retries=3, ignore_result=True)
def parse_rsses():
    r = parse_rsses.request
    if hasattr(r, 'task'):
        sql = """
        INSERT INTO bao_task_record(task_id, tast_name, user_id, argsrepr, kwargs, begin_at) 
        VALUES ('{task_id}', '{tast_name}', '{user_id}', '{argsrepr}', '{kwargs}', '{begin_at}') 
        ON DUPLICATE KEY UPDATE begin_at='{begin_at}';
        """.format(task_id=r.id,
                   tast_name=r.task,
                   user_id=0,
                   argsrepr=pymysql.escape_string(
                       str(r.args)),
                   kwargs=pymysql.escape_string(
                       str(r.kwargs)),
                   begin_at=get_unix_time_tuple())
        db.query(sql)
    sql = """
    SELECT bao_rss.rss_link FROM bao_rss WHERE bao_rss.rss_state = 1;
    """
    links = db.query(sql)
    for link in links:
        async_parser_feed(link['rss_link'])
    if hasattr(r, 'task'):
        sql = """
        UPDATE bao_task_record SET end_at='{end_at}', is_succ={is_succ} WHERE task_id='{task_id}'
        """.format(task_id=r.id, is_succ=int(True), end_at=get_unix_time_tuple())
        db.query(sql)
