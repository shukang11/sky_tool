import smtplib
from email.mime.text import MIMEText

#设置服务器所需信息
#163邮箱服务器地址
MAIL_HOST = 'smtp.163.com'

def prepare_message(title: str, content: str, sender: str, receiver: str):
    #设置email信息
    #邮件内容设置
    message = MIMEText(content,'plain','utf-8')
    #邮件主题       
    message['Subject'] = title
    #发送方信息
    message['From'] = sender 
    #接受方信息
    message['To'] = receiver
    return message

def send_messages(user, password, message: MIMEText) -> bool:
    try:
        smtpObj = smtplib.SMTP_SSL()
        smtpObj.connect(MAIL_HOST, 465) # 25 是SMTP端口号
        smtpObj.login(user, password)
        sender = message['From']
        receiver = message['To']
        smtpObj.sendmail(
            sender, receiver, message.as_string()
        )
        smtpObj.quit()
        return True
    except smtplib.SMTPException as e:
        print("error", e)
        return False