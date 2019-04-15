import requests

from ..views import api
from app.utils import response_succ
from app.utils import login_require

from app.utils.ext import request

from flask import url_for

@api.route('/help', methods=['GET'])
@login_require
def index():
    return response_succ(body="hahaha")


@api.route('/test', methods=['GET', 'POST'])
def test_f():
    params = request.values
    payload = {}
    payload['rec'] = request.url
    payload['params'] = params
    payload['host'] = request.host
    payload['scheme'] = request.scheme
    payload['url'] = url_for('api.task_parser_backend')
    return response_succ(body=payload)
