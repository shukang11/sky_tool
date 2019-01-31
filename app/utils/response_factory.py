# -*- coding: utf-8 -*-
"""

@file: response_factory.py
@time: 2019-01-26 09:31

"""

from flask import jsonify


def __check_request(request="") -> str:
    """
    检查返回的错误信息是否合规则
    :param request: 返回的请求地址
    :return: 如果请求的地址为空，则返回空字符串
    """
    methods = ['get', 'post', 'put', 'patch', 'delete', '*']
    request = request.lower()
    request = request.strip()
    if len(request) == 0:
        return ""

    for method in methods:
        if request.startswith(method):
            request = request.replace(method, method.upper())
            break
    else:
        request = "GET {}".format(request)
    return request


def __error_handler(msg=None, code=404, request="") -> dict:
    """
    将不正确的参数格式化返回
    :param msg: 错误信息
    :param code: 错误码
    :param request: 下一步的链接(可选)
    :return: 组装的字典对象
    """
    result = dict()
    request = __check_request(request)
    result["code"] = code
    if msg:
        result["msg"] = msg
    if len(request) > 0:
        result["request"] = request
    return result


def r400_invalid_requet(msg=None, code=400, request=""):
    """[POST/PUT/PATCH]：用户发出的请求有错误，服务器没有进行新建或修改数据的操作"""
    return jsonify(__error_handler(msg, code, request)), 400


def r401_unauthorized(msg=None, code=401, request=""):
    """[*]：表示用户没有权限（令牌、用户名、密码错误）。"""
    return jsonify(__error_handler(msg, code, request)), 401


def r403_forbidden(msg=None, code=403, request=""):
    return jsonify(__error_handler(msg, code, request)), 403


def r404_not_found(msg=None, code=401, request=""):
    return jsonify(__error_handler(msg, code, request)), 404


def r500_server_error(msg=None, code=401, request=""):
    return jsonify(__error_handler(msg, code, request)), 500


R401_UNAUTHORIZED = {}
R403_FORBIDDEN = {}
R404_NOT_FOUND = {}


def response_succ(status_code=200, body={}, header=None):
    success_codes = [200, 201, 202, 204]
    if status_code not in success_codes:
        raise ValueError("statusCode is not in successCodes")
    try:
        if body:
            body = jsonify(body)
    except Exception as _:
        raise ValueError("Unknown body")
    if header is None:
        header = {
            # 'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        }
    return body, status_code, header


def response_error(error_code=0, msg=None, http_code=0, header=None):
    """
    200 OK - [GET]：服务器成功返回用户请求的数据，该操作是幂等的（Idempotent）。
    201 CREATED - [POST/PUT/PATCH]：用户新建或修改数据成功。
    202 Accepted - [*]：表示一个请求已经进入后台排队（异步任务）
    204 NO CONTENT - [DELETE]：用户删除数据成功。
    400 INVALID REQUEST - [POST/PUT/PATCH]：用户发出的请求有错误，服务器没有进行新建或修改数据的操作，该操作是幂等的。
    401 Unauthorized - [*]：表示用户没有权限（令牌、用户名、密码错误）。
    403 Forbidden - [*] 表示用户得到授权（与401错误相对），但是访问是被禁止的。
    404 NOT FOUND - [*]：用户发出的请求针对的是不存在的记录，服务器没有进行操作，该操作是幂等的。
    406 Not Acceptable - [GET]：用户请求的格式不可得（比如用户请求JSON格式，但是只有XML格式）。
    410 Gone -[GET]：用户请求的资源被永久删除，且不会再得到的。
    422 Unprocesable entity - [POST/PUT/PATCH] 当创建一个对象时，发生一个验证错误。
    500 INTERNAL SERVER ERROR - [*]：服务器发生错误，用户将无法判断发出的请求是否成功。

    :return: 返回一个响应
    """
    from flask import request as r
    error_codes = [400, 401, 402, 403, 404, 406, 410, 500]
    if msg is None:
        raise ValueError("error Msg can't be None")
    if msg and http_code not in error_codes:
        raise ValueError("error and successCode can't both exists")
    if header is None:
        header = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Method': '*'
        }
    data = __error_handler(msg=msg,
                                   code=error_code,
                                   request="{0} {1}".format(r.method, r.path))

    return jsonify(data) or jsonify({"error": "cant jsonify"}), http_code, header
