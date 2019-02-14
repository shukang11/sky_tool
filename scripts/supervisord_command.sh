#!/bin/sh

pipenv shell
gunicorn -c gunicorn_config.py main:app