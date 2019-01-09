from functools import wraps
from app.utils.ext import request, db, jsonify
from app.utils import RespObj
from app.models import User, Role, Roles_Users

def login_require(func):
    """
    检测登录权限
    在执行 func 之前，会检查权限
    :param func:  被执行的 router_func
    """
    @wraps(func)
    def decorator_view(*args, **kwargs):
        params = request.values or request.get_json() or {}
        token = params.get('token') or params.get('token')
        if not token:
            return 'hello', 404
        # check
        user = User.get_user(req_token=token)
        if not user:
            return jsonify(RespObj(0,toast="请先登录").json())
        return func(*args, **kwargs)
    return decorator_view
