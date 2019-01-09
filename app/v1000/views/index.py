from flask import jsonify
from ..views import api
from app.utils.respObj import RespObj


@api.route('/help', methods=['GET'])
def index():
    resp = RespObj(1, "hihias")
    return jsonify(resp.json())