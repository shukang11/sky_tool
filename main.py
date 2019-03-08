import os
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple

from app import create_app as create_main_app
from app.utils.ext import celery_app

celery_app.config_from_object("celery_config")

main_app = create_main_app('default')
application = DispatcherMiddleware(main_app, {})


if __name__ == '__main__':
    run_simple("0.0.0.0", port=8091, application=application, use_reloader=True, use_debugger=True)
    # from chat import socketio
    # socketio.run(chat_app, port=8091)