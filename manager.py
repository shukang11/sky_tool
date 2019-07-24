import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import eventlet
from app import create_app as create_main_app

eventlet.monkey_patch(socket=True, select=True)

main_app = create_main_app(os.environ.get('FLASK_ENV') or 'default')
application = DispatcherMiddleware(main_app, {})

if __name__ == '__main__':
    from app.utils.ext import socket_app
    socket_app.run(main_app, port=8091, debug=True)
    with main_app.app_context() as app:
        celery_app.start()
