from app.utils.ext import Flask, render_template
from flask_socketio import SocketIO
from config import config

socketio = SocketIO()

def create_app(env: str) -> Flask:
    app = Flask(__name__)
    config_obj = config.get(env)
    app.config.from_object(config_obj)
    socketio.init_app(app)
    from chat.views import page
    app.register_blueprint(page)

    return app