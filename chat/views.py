from flask import render_template, Blueprint, Response
from flask_socketio import send, emit
from chat import socketio

page = Blueprint("page", __name__)

@socketio.on("client_event") # 应该是会独占一个端口，后续需要修改
def handle_client_event(json):
    emit("server_response", {'data': str(json)})

@page.route("/<string:file>", methods=["GET"])
def render_file(file="index.html"):
    return render_template(file)


@page.route("/large.csv")
def generate_large_csv():
    """
    下面是一个简单的视图函数，这一视图函数实时生成大量的 CSV 数据， 
    这一技巧使用了一个内部函数，这一函数使用生成器来生成数据，
    并且稍后激发这个生成器函数时，把返回值传递给一个 response 对象
    """
    def generate():
        for row in range(0, 10000):
            yield ','.join(str(row)) + '\n'
    return Response(generate(), mimetype='text/csv')