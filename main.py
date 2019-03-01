import os
from app import create_app
from app.utils.ext import render_template, request
from app.utils.response_factory import response_succ
from app.utils import login_require

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8091, debug=True)