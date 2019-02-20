from ..views import api
from app.utils import response_succ
from app.utils import login_require

from app.utils.ext import request

@api.route('/help', methods=['GET'])
@login_require
def index():
    return response_succ(body="hahaha")


@api.route('/test', methods=['GET', 'POST'])
def test_f():
    params = request.values
    print(params)
    return response_succ(body={'rec': '/test', 'par': params})
