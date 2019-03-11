# -*- coding: utf-8 -*-
"""

@file: tool_view.py
@time: 2019-01-28 11:45

"""
import hashlib
from flask import request
from ..views import api
from app.utils import response_succ, CommonError
from app.utils.ext import socket_app

@api.route("/tool/encryption/<string:encrypt_type>", methods=["POST", "GET"])
def encryption(encrypt_type: str = "md5"):
    """
    指定加密方式
    :param encrypt_type: encryption type default is "md5"...
    support
    'sha1','md5', 'sha256', 'sha224', 'sha512', 'sha384', 'blake2b',
    'blake2s', 'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
    'shake_128', 'shake_256'
    :return:
    """
    params = request.values  or request.get_json() or {}
    source = params.get("source")
    if not source:
        return CommonError.get_error(40000)

    code: str = source
    encrypt_func = getattr(hashlib, encrypt_type, None) or None
    if not encrypt_func:
        return CommonError.get_error(40000)
    result = encrypt_func(code.encode('utf-8')).hexdigest()
    result_map = dict()
    result_map["source"] = source
    result_map["target"] = result
    result_map["type"] = encrypt_type
    return response_succ(body=result_map)


@socket_app.on('rec_client')
def handle_client_message(msg):
    print(msg['data'])
    socket_app.emit('resp_server', {'data': 'i hear you' + str(msg['data'])})
