import os
from app import create_app
from flask import jsonify

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.route('/', methods=['GET'])
def routeMap():
    return jsonify({
        "api/v1000": "api/v1000"
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8091, debug=True)