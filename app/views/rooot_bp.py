from app.views import root

@root.route('/<string:file>')
def root_file_handle(file: str='index.html'):
    return render_template(file)
