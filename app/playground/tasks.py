# -*- coding: utf-8 -*-
"""

@file: tasks.py
@time: 2019-01-28 15:32

"""

"""
这是一个分布式计算的框架，不学习，空置
"""
from celery import Celery
import redis

pool = redis.ConnectionPool(port=6379)
redisClient = redis.Redis(connection_pool=pool)

app = Celery("tasks", broker="redis://localhost")

@app.task
def add(x, y):
    return x + y
