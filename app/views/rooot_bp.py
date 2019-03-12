from app.views import root
from app.utils.ext import render_template

@root.route('/<string:file>')
def root_file_handle(file: str='index.html'):
    return render_template(file)
