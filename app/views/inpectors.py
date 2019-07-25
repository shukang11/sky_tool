import logging

from app.utils.ext import request, g
from app.models import User

from ..views import api

@api.before_request
def api_before_request():
    ip = request.remote_addr
    path = request.path
    params = request.values.to_dict() or request.get_json() or {}
    userId = ""
    # 获得用户
    token = params.get("token")
    if token:
        # check
        user: User = User.get_user(token=token)
        if user: userId = str(user.id)
    logging.info('{ip}|{userId}|{path}|{params}'.format(ip=ip, userId=userId, path=path, params=str(params)))
