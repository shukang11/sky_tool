# -*- coding: utf-8 -*-
'''

@file: strings.py
@time: 2019-01-25 17:51

'''
import hashlib
import random
import datetime
import time


def get_unix_time_tuple(date=datetime.datetime.now(), millisecond=False):
    """ get time tuple
    
    get unix time tuple, default `date` is current time

    Args:
        date: datetime, default is datetime.datetime.now()
        millisecond: if True, Use random three digits instead of milliseconds, default id False 

    Return:
        a str type value, return unix time of incoming time
    """
    time_tuple = time.mktime(date.timetuple())
    time_tuple = round(time_tuple * 1000) if millisecond else time_tuple
    second = str(int(time_tuple))
    return second


def get_date_from_time_tuple(unix_time=get_unix_time_tuple(), formatter='%Y-%m-%d %H:%M:%S') -> time:
    """ translate unix time tuple to time
    
    get time from unix time

    Args:
        unix_time: unix time tuple
        formatter: str time formatter

    Return:
        a time type value, return time of incoming unix_time
    """
    if len(unix_time)  == 13:
        unix_time = int(unix_time) / 1000
    t = int(unix_time)
    time_locol = time.localtime(t)
    return time.strftime(formatter, time_locol)


def getmd5(code):
    """ return md5 value of incoming code
    
    get md5 from code

    Args:
        code: str value

    Return:
        return md5 value of code
    """
    if code:
        md5string = hashlib.md5(code.encode('utf-8'))
        return md5string.hexdigest()
    return None

def get_random_num(digit=6):
    """ get a random num
    
    get random num 

    Args:
        digit: digit of the random num, limit (1, 32)

    Return:
        return Generated random num
    """
    if digit is None:
        digit = 1
    digit = min(max(digit, 1), 32)# 最大支持32位
    result = ""
    while len(result) < digit:
        append = str(random.randint(1, 9))
        result = result + append
    return result

def is_emoji(content: str):
    """ judge str is emoji

    Args: str type 

    Return : Bool type , return True if is Emoji , else False
    """
    if not content:
        return False
    if u"\U0001F600" <= content and content <= u"\U0001F64F":
        return True
    elif u"\U0001F300" <= content and content <= u"\U0001F5FF":
        return True
    elif u"\U0001F680" <= content and content <= u"\U0001F6FF":
        return True
    elif u"\U0001F1E0" <= content and content <= u"\U0001F1FF":
        return True
    else:
        return False

def contain_emoji(content: str):
    """ judge str contain emoji str

    Args: str type

    Return : Bool type, return True if contain Emoji, else False
    """
    for c in content:
        if is_emoji(c):
            return True
    return False

def get_domain(url: str):
    """ get domain from url by given
    
    Args: str type
    Return: str type, return domain if can get
    """
    from urllib.parse import urlparse
    parsed_uri = urlparse(url)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    return domain