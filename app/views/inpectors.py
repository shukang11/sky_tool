import logging

from app.utils.ext import request, g
from app.models import User

from ..views import api

@api.before_request
def api_before_request():
    ip = request.remote_addr
    path = request.path
    params = request.values.to_dict() or request.get_json() or {}
    logging.info('{ip}|{path}|{params}'.format(ip=ip, path=path, params=str(params)))
