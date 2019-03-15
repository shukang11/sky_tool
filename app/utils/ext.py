from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.mssql import FLOAT, TEXT, INTEGER, DECIMAL, SMALLINT
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, \
    UnmappedColumnError
from sqlalchemy import Sequence
import flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, g, render_template, current_app
from flask_uploads import UploadSet, DEFAULTS
from flask_socketio import SocketIO
import redis
from apscheduler.schedulers.background import BackgroundScheduler

# celery_app = Celery('app', include=['app.command.tasks'])
# celery_app.config_from_object("celery_config")

# class FlaskCelery(Celery):

#     def __init__(self, *args, **kwargs):
#         super(FlaskCelery, self).__init__(*args, **kwargs)
#         self.patch_task()
#         if 'app' in kwargs:
#             self.init_app(kwargs['app'])

#     def patch_task(self):
#         TaskBase = self.Task
#         _celery = self

#         class ContextTask(TaskBase):
#             abstract = True

#             def __call__(self, *args, **kwargs):
#                 if flask.has_app_context():
#                     return TaskBase.__call__(self, *args, **kwargs)
#                 else:
#                     with _celery.app.app_context():
#                         return TaskBase.__call__(self, *args, **kwargs)
        
#         self.Task = ContextTask
        
#     def init_app(self, app: Flask):
#         self.app = app
#         self.config_from_object(app.config)

flask_app = Flask(__name__)
# 定时执行
scheduler = BackgroundScheduler()
socket_app = SocketIO()
db = SQLAlchemy()

fileStorage = UploadSet(extensions=DEFAULTS)

pool = redis.ConnectionPool(port=6379)
redisClient = redis.Redis(connection_pool=pool)

__all__ = ["Column", "ForeignKey", "String", "FLOAT",
           "TEXT", "INTEGER", "DECIMAL", "SMALLINT",
           "NoResultFound", "MultipleResultsFound",
           "UnmappedColumnError", "Sequence",
           "Flask", "request", "redisClient", "db",
           "fileStorage", "jsonify", "g", "render_template",
           "scheduler", "current_app", "socket_app", "flask_app"]