from __future__ import absolute_import
import os
from celery import Celery
import records
from dynaconf import settings
from config import config

env = os.environ.get('FLASK_ENV') or 'default'
config_obj = config[env]

celery_app = Celery('tasks')
celery_app.config_from_object(config_obj)
url = settings.get('SQLALCHEMY_DATABASE_URI')
db = records.Database(url)
