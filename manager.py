import os
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
import eventlet
from app import create_app as create_main_app

from celery_tasks import celery_app

if os.environ.get('FLASK_ENV') == "production":
    eventlet.monkey_patch()

main_app = create_main_app(os.environ.get('FLASK_ENV') or 'default')
application = DispatcherMiddleware(main_app, {})

if __name__ == '__main__':
    # run_simple("0.0.0.0", port=8091, application=application, use_reloader=True, use_debugger=True)
    from app.utils.ext import socket_app
    socket_app.run(main_app, port=8091, debug=True)
    with main_app.app_context() as app:
        celery_app.start()
