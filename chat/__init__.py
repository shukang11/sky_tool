from app.utils.ext import Flask, render_template
from config import config

def create_app(env: str) -> Flask:
    app = Flask(__name__)
    config_obj = config.get(env)
    app.config.from_object(config_obj)

    from chat.views import page
    app.register_blueprint(page)

    return app