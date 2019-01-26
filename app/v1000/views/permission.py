# -*- coding: utf-8 -*-
"""

@file: permission.py
@time: 2019-01-26 10:25

"""

from flask import request
from ..views import api
from app.utils import response_succ, CommonError, UserError, login_require


@api.route("/permission/delivery", methods=["POST"])
def delivery_authority():
    params = request.values or request.get_json()
    pass