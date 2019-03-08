#!/bin/sh

pipenv run /gunicorn -c gunicorn_config.py main:application

# 启动 celery 服务
pipenv run celery -A main worker -l info