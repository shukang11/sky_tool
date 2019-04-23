from functools import wraps
from app.utils.ext import request, db, jsonify, g
from app.utils import CommonError, UserError
from app.models import User


def login_require(func):
    """
    检测登录权限
    在执行 func 之前，会检查权限
    :param func:  被执行的 router_func
    """
    @wraps(func)
    def decorator_view(*args, **kwargs):
        params = request.values or request.get_json() or {}
        token = params.get("token")
        if not token:
            return CommonError.get_error(43000)
        # check
        user = User.get_user(token=token)
        if not user:
            return UserError.get_error(40204)
        g.current_user = user
        return func(*args, **kwargs)
    return decorator_view


def pages_info_require(func):
    """ 处理请求前的页面信息 """
    @wraps(func)
    def decorator_view(*args, **kwargs):
        params = request.values or request.get_json() or {}
        pages = int(params.get('pages'))
        limit = int(params.get('limit'))
        info = {}
        info['limit'] = max(limit, 1)
        info['offset'] = max(pages, 0) * limit
        info['pages'] = max(pages, 0)
        g.pageinfo = info
        return func(*args, **kwargs)
    return decorator_view