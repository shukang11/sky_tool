import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import eventlet
from app import create_app as create_main_app

eventlet.monkey_patch(socket=True, select=False)

main_app = create_main_app(os.environ.get('FLASK_ENV') or 'default')
application = DispatcherMiddleware(main_app, {})

if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') is "production":
        return
    main_app.run(port=8091)
