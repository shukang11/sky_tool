from app.views import root
from app.utils.ext import render_template, Response
from app.utils import login_option

@root.route('/<string:file>')
def root_file_handle(file: str='index.html'):
    print("render: " + str(file))
    return render_template(file)
