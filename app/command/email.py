# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from time import time
from contextlib import contextmanager

class Connection(object):

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

    def configure_host(self):
        if self.mail.use_ssl:
            host = smtplib.SMTP_SSL(self.mail.server, self.mail.port)
        else:
            host = smtplib.SMTP(self.mail.server, self.mail.port)
            
        if self.mail.username and self.mail.password:
            host.login(self.mail.username, self.mail.password)
        return host

    def send(self, message, envelop_from=None):
        """ 验证并发送 """
        assert message.send_to, "没有收件人"
        assert message.sender, "没有发件人"

        if not message.date:
            message.date = str(time())

        if not self.host:
            raise ValueError
        self.host.sendmail(
            message.sender,
            message.send_to,
            message.as_string(),
        )

        self.number_emails += 1

        if self.number_emails == self.mail.max_emails:
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

    def __init__(self, subject='', recipients=[], body=None, sender=None, date=None, charset=None, extra_headers=None):
        self.subject = subject
        self.recipients = recipients or []
        self.sender = sender
        self.body = body
        self.date = date
        self.charset = charset
        self.extra_headers = extra_headers or []

    @property
    def send_to(self):
        return set(self.recipients)

    def _mimetext(self, text, subtype='plain'):
        charset = self.charset or 'utf-8'
        return MIMEText(text, _subtype=subtype, _charset=charset)

    def _message(self):
        msg = self._mimetext(self.body)
        
        if self.subject:
            msg["Subject"] = self.subject
        
        msg["From"] = self.sender
        msg["To"] = ', '.join(list(set(self.recipients)))

        msg["Data"] = self.date

        if self.extra_headers:
            for (k, v) in self.extra_headers.items():
                msg[k] = v
        
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
    def __init__(self, server: str, username: str, password: str, port: int, use_ssl:bool, sender: str, max_emails: int):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.sender = sender
        self.max_emails = max_emails
    
    def connect(self):
        return Connection(self)

    def send(self, message):
        with self.connect() as connection:
            message.send(connection)
    
    def send_message(self, *args, **kwargs):
        self.send(Message(*args, **kwargs))