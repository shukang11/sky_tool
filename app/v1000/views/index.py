from ..views import api
from app.utils import response_succ
from app.utils import login_require


@api.route('/help', methods=['GET'])
@login_require
def index():
    return response_succ(body="hahaha")