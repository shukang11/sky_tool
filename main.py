import os
from app import create_app
from app.utils.ext import render_template
from app.utils import login_require

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.route('/', methods=['GET'])
@login_require
def routeMap():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8091, debug=True)