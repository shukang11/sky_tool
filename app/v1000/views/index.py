from flask import jsonify
from ..views import api
from app.utils.respObj import RespObj
from  app.utils import login_require


@api.route('/help', methods=['GET'])
@login_require
def index():
    resp = RespObj(1, "hihias")
    return jsonify(resp.json())