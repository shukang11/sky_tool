# -*- coding: utf-8 -*-
'''

@file: strings.py
@time: 2019-01-25 17:51

'''
import hashlib
import random
import datetime
import time


def get_unix_time_tuple(date=datetime.datetime.now()):
    """获得unix 时间戳"""
    return time.mktime(date.timetuple())


def get_date_from_time_tuple(unix_time=get_unix_time_tuple(), formatter='%Y-%m-%d %H:%M:%S') -> time:
    """时间戳转换成时间"""
    t = int(unix_time)
    time_locol = time.localtime(t)
    return time.strftime(formatter, time_locol)


def getmd5(code):
    """获得md5加密的字符串"""
    if code:
        md5string = hashlib.md5(code.encode('utf-8'))
        return md5string.hexdigest()
    return None

def get_random_num(digit=6):
    """获得一个随机数"""
    if digit is None:
        digit = 1
    digit = min(digit, 32)# 最大支持10位
    result = ""
    while len(result) < digit:
        append = str(random.randint(1, 9))
        result = result + append
    return result