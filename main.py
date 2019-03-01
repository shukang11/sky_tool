import os
from app import create_app
from app.utils.ext import render_template, request
from app.utils.response_factory import response_succ
from app.utils import login_require

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.route('/<string:file>', methods=['GET'])
def routeMap(file: str):
    return render_template(file)

@app.route('/test', methods=['GET', 'POST'])
def on_test():
    params = request.values
    return response_succ(body=params or {"r": "on test"})

if __name__ == '__main__':
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='0.0.0.0', port=8091, debug=True)