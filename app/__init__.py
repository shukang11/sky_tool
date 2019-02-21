from flask_uploads import configure_uploads
from app.utils.ext import Flask, db, fileStorage, scheduler, current_app
from config import config, Config, root_dir
import os


def log():
    current_app.logger.debug("scheduler is running")


__all__ = ['create_app']

route_list = []


def fetch_route(blueprint, prefix=None):
    t = (blueprint, prefix)
    route_list.append(t)


def register_blueprint(app):
    app_dir = os.path.join(root_dir, 'app')
    for routes in os.listdir(app_dir):
        rou_path = os.path.join(app_dir, routes)
        if (not os.path.isfile(rou_path)) \
                and routes != 'static' \
                and routes != 'templates' \
                and not routes.startswith('__'):
            __import__('app.' + routes)

    print(route_list)
    for blueprints in route_list:
        if blueprints[1] is not None:
            app.register_blueprint(blueprints[0], url_prefix=blueprints[1])
        else:
            app.register_blueprint(blueprints[0])


def create_table(config_name, app):
    if config_name is not 'production':
        from app.models import __all__
        with app.test_request_context():
            db.create_all()


def create_app(env: str) -> Flask:
    assert(type(env) is str)
    config_obj = config[env]
    app = Flask(__name__)
    app.config.from_object(config_obj)
    db.init_app(app)
    config_obj.init_app(app)
    # 注册插件
    register_blueprint(app)
    configure_uploads(app, fileStorage)
    create_table(env, app)
    # 开启定时任务
    if env == "production":
        scheduler.add_job(log, 'interval', seconds=1000)
        scheduler.start()
    return app
