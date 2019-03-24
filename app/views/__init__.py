from flask import Blueprint, render_template
import app

api = Blueprint('api', __name__)
root = Blueprint('root', __name__)

from app.views import index
from app.views import permission
from app.views import todo
from app.views import tool_view
from app.views import upload
from app.views import user
from app.views import rss
from app.views import root_bp

# 注册蓝图
app.fetch_route(api, '/api')
app.fetch_route(root, '/')
