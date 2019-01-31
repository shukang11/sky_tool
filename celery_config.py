# -*- coding: utf-8 -*-
"""

@file: celery_config.py
@time: 2019-01-28 15:42

"""
"""
分布式 计算框架配置 
"""
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']
# 限制此类型的任务， 每分钟只处理10个
CELERY_ANNOTATIONS = {
    'tasks.add': {'rate_limit': '10/m'}
}