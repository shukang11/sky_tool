# -*- coding: utf-8 -*-
from typing import Optional, List, ClassVar, Text, Dict, Set
import os
import smtplib
from smtplib import SMTP
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from time import time
from contextlib import contextmanager

def get_file_path(file: str) -> Optional[str]:
    from config import config, Config
    env = os.environ.get('FLASK_ENV')
    c: Config = config.get(env)
    return os.path.join(os.path.abspath(c.UPLOAD_FOLDER), 'files', file)

class Connection(object):
    mail: ClassVar
    number_emails: int

    """ Handles connections to hosts. """

    def __init__(self, mail):
        self.mail = mail

    def __enter__(self):
        # 调用 with 时 调用 __enter__
        self.host = self.configure_host()
        self.number_emails = 0
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.host:
            self.host.quit()

    def configure_host(self) -> SMTP:
        if self.mail.use_ssl:
            host = smtplib.SMTP_SSL(self.mail.server, self.mail.port)
        else:
            host = smtplib.SMTP(self.mail.server, self.mail.port)
        # host.set_debuglevel(1)
        if self.mail.username and self.mail.password:
            host.login(self.mail.username, self.mail.password)
        return host

    def send(self, message: ClassVar, envelop_from=None):
        """ 验证并发送 """
        assert message.send_to, "没有收件人"
        assert message.sender, "没有发件人"

        message.date = str(time())

        if not self.host:
            raise ValueError
        self.host.sendmail(
            message.sender,
            message.send_to,
            message.as_string(),
        )

        self.number_emails += 1

        if self.number_emails >= self.mail.max_emails:
            self.number_emails = 0
            self.host.quit()
            self.host = self.configure_host()

    def send_message(self, *args, **kwargs):
        self.send(*args, **kwargs)


class Message(object):
    """Encapsulates an email message.
    :param subject: email subject header
    :param body: plain text message
    :param recipients: recipients
    :param sender: email sender address
    :param date: send date
    :param charset: message character set
    :param extra_headers: A dictionary of additional headers for the message
    """
    subject = str
    recipients = List[str]
    body = Optional[str]
    sender = Optional[str]
    extra_headers = Dict[str, str]
    attaches = Optional[List[str]] # 附件

    _charset: Optional[str] = 'utf-8'

    def __init__(self,
                 subject: str,
                 recipients: Optional[List[str]],
                 body: Optional[str],
                 sender: Optional[str],
                 attaches: Optional[List[str]],
                 extra_headers: Optional[Dict[str, str]] = None):
        self.subject = subject
        self.recipients = recipients or []
        self.sender = sender
        self.body = body
        self.attaches = attaches
        self.extra_headers = extra_headers or {}

    @property
    def send_to(self) -> Set:
        return set(self.recipients)

    def _mimetext(self, text, subtype='plain') -> MIMEText:
        message = MIMEText(text, _subtype=subtype, _charset=self._charset)
        return message

    def _message(self) -> MIMEMultipart:
        message = MIMEMultipart()
        message["Subject"] = Header(self.subject).encode()
        message["From"] = Header('SKY_TOOL<{sender}>'.format(sender=self.sender), self._charset)
        recs: List[str] = list(set(self.recipients))
        resc_maped: List[str] = []
        for r in recs:
            resc_maped.append("jack<{x}>".format(x=r))
        to_resc = ', '.join(resc_maped)
        message["To"] = Header(to_resc)
        message.attach(self._mimetext(self.body))
        if self.extra_headers:
            for (k, v) in self.extra_headers.items():
                msg[k] = v
        if self.attaches:
            for path in self.attaches:
                path = get_file_path(path)
                print(path)
                # attach = MIMEText(open(path, 'r').read(), 'base64', 'utf-8')
                attach = MIMEApplication(open(path, 'rb').read())
                attach["Content-Type"] = 'application/octet-stream'# 这里的filename可以任意写，写什么名字，邮件中显示什么名字
                attach["Content-Disposition"] = 'attachment; filename="{}"'.format(path.split('/')[-1])
                message.attach(attach)
        return message

        return msg

    def as_string(self):
        return self._message().as_string()

    def as_bytes(self):
        return self._message().as_bytes()

    def __str__(self):
        return self.as_string()

    def __bytes__(self):
        return self.as_bytes()

    def send(self, connection: Connection):
        connection.send(self)

    def add_recipient(self, recipient):
        self.recipients.append(recipient)


class Mail(object):
    server: str
    username: str
    password: str
    port: int
    use_ssl: bool
    sender: str
    max_emails: int

    def __init__(self,
                 server: str,
                 username: str,
                 password: str,
                 port: int,
                 use_ssl: Optional[bool],
                 sender: str,
                 max_emails: Optional[int]):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl or False
        self.sender = sender
        self.max_emails = max_emails or 3

    def connect(self) -> Connection:
        return Connection(self)

    def send(self, message: Message):
        with self.connect() as connection:
            message.send(connection)

    def send_message(self, *args, **kwargs):
        self.send(Message(*args, **kwargs))
