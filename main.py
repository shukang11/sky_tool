import os
from app import create_app as create_main_app
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple

from app.utils.ext import render_template, request
from app.utils.response_factory import response_succ
from app.utils import login_require


main_app = create_main_app('default')

application = DispatcherMiddleware(main_app, {
})

if __name__ == '__main__':
    # main_app.run("0.0.0.0", port=8091, debug=True)
    run_simple("0.0.0.0", port=8091, application=application, use_reloader=True, use_debugger=True)