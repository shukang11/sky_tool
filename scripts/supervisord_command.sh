#!/bin/sh

pipenv run %(ENV_HOME)/.venv/bin/gunicorn --worker-class eventlet -c gunicorn_config.py manager:application

# 启动 celery 服务(消费者)
pipenv run %(ENV_HOME)/.venv/bin/celery -A celery_tasks:celery_app worker -l info
# 启动 celery beat 来执行定时任务等
pipenv run %(ENV_HOME)/.venv/bin/celery beat -A celery_tasks