from functools import wraps
from app.utils.ext import request, db, jsonify, g, session
from app.utils import CommonError, UserError
from app.models import User

def login_option(func):
    
    @wraps(func)
    def decorator_view(*args, **kwargs):
        user = get_user_from_request(request, False)
        if user is User:
            g.current_user = user
        
        return func(*args, **kwargs)
    return decorator_view

def login_require(func):
    """
    检测登录权限
    在执行 func 之前，会检查权限
    :param func:  被执行的 router_func
    """
    @wraps(func)
    def decorator_view(*args, **kwargs):
        userOrError: any = get_user_from_request(request, True)
        if not userOrError:
            return UserError.get_error(40204)
        if isinstance(userOrError, User):
            g.current_user = userOrError
        else:
            return userOrError
        return func(*args, **kwargs)
    return decorator_view

def get_user_from_request(request, isforce: bool) -> any:
    params = request.values or request.get_json() or {}
    alise: str = "token"
    token = params.get(alise)
    if not token:
        token = session.get(alise)
    if not token:
        token = request.cookies.get(alise)
    if not token:
        if isforce:
            return CommonError.get_error(43000)
        else:
            return CommonError.get_error(40000)  
    user = User.get_user(token=token)
    return user
    
def pages_info_require(func):
    """ 处理请求前的页面信息 """
    @wraps(func)
    def decorator_view(*args, **kwargs):
        params = request.values or request.get_json() or {}
        pages = int(params.get('pages') or 0)
        limit = int(params.get('limit') or 0)
        info = {}
        info['limit'] = max(limit, 1)
        info['offset'] = max(pages, 0) * limit
        info['pages'] = max(pages, 0)
        g.pageinfo = info
        return func(*args, **kwargs)
    return decorator_view