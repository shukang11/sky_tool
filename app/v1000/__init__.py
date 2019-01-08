from flask import Blueprint
import app

api = Blueprint('api1_0', __name__)

from .views import index
from .views import upload
# 注册蓝图
app.fetch_route(api, '/api/v1000')
