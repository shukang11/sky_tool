#!/bin/sh

pipenv run %(ENV_HOME)/.venv/bin/gunicorn -c gunicorn_config.py main:application

# 启动 celery 服务
pipenv run %(ENV_HOME)/.venv/bin/celery -A main worker -l info