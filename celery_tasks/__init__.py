from __future__ import absolute_import
import os
from celery import Celery
import records
from config import config

env = os.environ.get('FLASK_ENV') or 'default'

config_obj = config[env]

celery_app = Celery('tasks')
celery_app.config_from_object(config_obj)
url = getattr(config_obj, 'SQLALCHEMY_DATABASE_URI')
db = records.Database(url)

    # TaskBase = celery.Task
    # class ContextTask(TaskBase):
    #     abstract = True
    #     def __call__(self, *args, **kwargs):
    #         with app.app_context():
    #             return TaskBase.__call__(self, *args, **kwargs)
    # celery.Task = ContextTask
