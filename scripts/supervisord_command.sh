#!/bin/sh

pipenv shell
gunicorn -c gunicorn_config.py main:application

# 启动 celery 服务
celery -A tasks worker -l info