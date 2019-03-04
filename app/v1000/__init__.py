from flask import Blueprint
import app

api = Blueprint('api1_0', __name__)

from .views import index
from .views import permission
from .views import todo
from .views import tool_view
from .views import upload
from .views import user
from .views import rss

# 注册蓝图
app.fetch_route(api, '/api/v1000')
