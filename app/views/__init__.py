from flask import Blueprint
import app

api = Blueprint('api1_0', __name__)

from app.views import index
from app.views import permission
from app.views import todo
from app.views import tool_view
from app.views import upload
from app.views import user
from app.views import rss

# 注册蓝图
app.fetch_route(api, '/api')
