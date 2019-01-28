# -*- coding: utf-8 -*-
"""

@file: tasks.py
@time: 2019-01-28 15:32

"""

from celery import Celery
import redis

pool = redis.ConnectionPool(port=6379)
redisClient = redis.Redis(connection_pool=pool)

app = Celery("tasks", broker="redis://localhost")

@app.task
def add(x, y):
    return x + y
