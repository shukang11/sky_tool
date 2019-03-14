# -*- coding: utf-8 -*-
"""

@file: celery_config.py
@time: 2019-01-28 15:42

"""
"""
分布式 计算框架配置 
"""
"""Celery 配置"""
from datetime import timedelta

# 导入Task所在的模块，所有使用celery.task装饰器装饰过的函数，所需要把所在的模块导入
# 我们之前创建的几个测试用函数，都在handlers.async_tasks和handlers.schedules中
# 所以在这里需要导入这两个模块，以str表示模块的位置，模块组成tuple后赋值给CELERY_IMPORTS
# 这样Celery在启动时，会自动找到这些模块，并导入模块内的task
CELERY_IMPORTS = ('app.command.tasks')

# 为Celery设定多个队列，CELERY_QUEUES是个tuple，每个tuple的元素都是由一个Queue的实例组成
# 创建Queue的实例时，传入name和routing_key，name即队列名称
# CELERY_QUEUES = {
#         "app_task_email": { "exchange": "app_task_email" },
#         "app_task_parser": { "exchange": "app_task_parser" },
#         "app_task_calculate": { "exchange": "app_task_calculate" },
#     }
# 最后，为不同的task指派不同的队列
# 将所有的task组成dict，key为task的名称，即task所在的模块，及函数名
# 如async_send_email所在的模块为handlers.async_tasks
# 那么task名称就是handlers.async_tasks.async_send_email
# 每个task的value值也是为dict，设定需要指派的队列name，及对应的routing_key
# 这里的name和routing_key需要和CELERY_QUEUES设定的完全一致
# CELERY_ROUTES = (
#     'app.command.tasks.add': {'queue': 'app_task_calculate'},
#     'app.command.tasks.mul': {'queue': 'app_task_calculate'},
#     'app.command.tasks.async_email_to': {'queue': 'app_task_email'},
#     'app.command.tasks.async_parser_feed': {'queue': 'app_task_parser'},
# )

CELERY_RESULT_BACKEND = 'redis://localhost:6379'

BROKER_URL = 'redis://localhost:6379/0'

CELERY_TIMEZONE='Asia/Shanghai'

CELERY_TASK_SERIALIZER = 'json'

CELERY_RESULT_SERIALIZER = 'json'

CELERY_ACCEPT_CONTENT=['json']
# 是否忽略结果
CELERY_IGNORE_RESULT=False

# 定义定时任务
CELERYBEAT_SCHEDULE = {
    # 给计划任务取一个独一无二的名字吧
    'every-30-seconds': {
        # task就是需要执行计划任务的函数
         'task': 'app.command.tasks.add',
         # 配置计划任务的执行时间，这里是每300秒执行一次
         'schedule': timedelta(seconds=300),
         # 传入给计划任务函数的参数
         'args': {'x': 1, 'y': 3}
    }
}

# 限制此类型的任务， 每分钟只处理10个
CELERY_ANNOTATIONS = {
    'app.command.tasks.add': {'rate_limit': '10/m'}
}