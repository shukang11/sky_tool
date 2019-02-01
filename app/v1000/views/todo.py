from flask import request
from ..views import api
from app.utils import response_succ, CommonError, get_unix_time_tuple, login_require
from app.utils.ext import g
from app.models import db, TodoModel

@api.route("/todo/add", methods=["POST"])
@login_require
def add_todo():
    parasm = request.values
    title = parasm.get("title")
    todo = TodoModel()
    todo.todo_title = title
    todo.add_time = get_unix_time_tuple()
    todo.todo_state = 1
    todo.bind_user_id = g.current_user.id
    db.session.add(todo)
    db.session.commit()
    result = {
        "todo_id": todo.todo_id
    }
    return response_succ(body=result)


@api.route("todo/finish", methods=["POST"])
@login_require
def finish_todo():
    params = request.values
    todo_id = params.get("todo_id")
    todo = db.session.query(TodoModel).filter_by(todo_id=todo_id).one()
    if not todo:
        return CommonError.get_error(44000)
    todo.todo_state = 2
    db.session.commit()
    result = {
        "todo_id": todo.todo_id,
        "todo_title": todo.todo_title,
        "todo_state": todo.todo_state
    }
    return response_succ(body=result)


@api.route("todo/remove", methods=["POST"])
@login_require
def remove_todo():
    params = request.values
    todo_id = params.get("todo_id")
    todo = db.session.query(TodoModel).filter_by(todo_id=todo_id).one()
    if not todo:
        return CommonError.get_error(44000)
    todo.todo_state = 2
    db.session.commit()
    result = {
        "todo_id": todo.todo_id,
        "todo_title": todo.todo_title,
        "todo_state": todo.todo_state
    }
    return response_succ(body=result)