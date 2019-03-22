# sky_tool

[![Build Status](https://travis-ci.org/jiazifa/sky_tool.svg?branch=master)](https://travis-ci.org/jiazifa/sky_tool)

工具页 需要配合[sky_web](https://github.com/jiazifa/sky_tool_web)

# 安装环境

## python 3.6+

## 1. 安装 [Pipenv](https://github.com/pypa/pipenv)

[参考链接](https://pipenv.readthedocs.io/en/latest/install/)

## 2. 安装依赖

`PIPENV_VENV_IN_PROJECT=true pipenv install --skip-lock`

## 3.使用 gunicorn 启动

`gunicorn -c gunicorn_config.py manager:application`

如果想使用 eventlet

`gunicorn --worker-class eventlet -c gunicorn_config.py manager:application`