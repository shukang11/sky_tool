#!/bin/sh

pipenv run %(ENV_HOME)/.venv/bin/gunicorn -c gunicorn_config.py main:application

# 启动 celery 服务
pipenv run %(ENV_HOME)/.venv/bin/celery -A celery_tasks:celery worker -l info