from flask import request
from ..views import api
from app.utils import response_succ, CommonError, get_unix_time_tuple, login_require
from app.utils.ext import g, NoResultFound
from app.models import db, TodoModel


@api.route("/todo/add", methods=["POST"])
@login_require
def add_todo():
    """ add todo by parameters

    try to add a todo to todolist,you can just set the todo title.

    Args:
        title: title of the todo item

    Returns:
        a dict mapping keys to the index of the todo item just added.
        example:
        {"todo_id": 6}

    """

    params = request.values or request.get_json() or {}
    title = params.get("title")
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


def set_todo_state(todo_id: int, state: int) -> any:
    """ change a todo item state

    try to modify a todo_state, option (1, 2, 3)

    Args:
        todo_id: the index of the todo item you wanna change.
        state: state value, 1: undo, 2: done, 3: removed

    Returns:
        a dict mapping keys to the structure of the todo item just changed, if change failed, return None.
        example:
        {
            "todo_id": 4,
            "todo_title": "test todo",
            "todo_state": 2
        }

    Raises:
        NoResultFound: An error occurred when A database result was required but none was found.

    """

    result = None
    try:
        todo = db.session.query(TodoModel).filter_by(todo_id=todo_id).one()
        if not todo:
            return result
        todo.todo_state = state
        db.session.commit()
        result = {
            "todo_id": todo.todo_id,
            "todo_title": todo.todo_title,
            "todo_state": todo.todo_state
        }
    except NoResultFound as e:
        result = None
    return result


@api.route("todo/finish", methods=["POST"])
@login_require
def finish_todo():
    params = request.values or request.get_json() or {}
    todo_id = params.get("todo_id")
    result = set_todo_state(todo_id, 2)
    if not result:
        return CommonError.get_error(40000)
    return response_succ(body=result)


@api.route("todo/remove", methods=["POST"])
@login_require
def remove_todo():
    params = request.values or request.get_json() or {}
    todo_id = params.get("todo_id")
    result = set_todo_state(todo_id, 3)
    if not result:
        return CommonError.get_error(40000)
    return response_succ(body=result)


@api.route("todo/filter/<string:filter>", methods=["POST"])
@login_require
def filter_todo(filter: str = None):
    params = request.values or request.get_json() or {}
    option_filter = filter or "all"
    todos = db.session.query(TodoModel).filter(
        TodoModel.bind_user_id == g.current_user.id)

    if option_filter == "undo":
        todos = todos.filter(TodoModel.todo_state == 1).all()
    if option_filter == "done":
        todos = todos.filter(TodoModel.todo_state == 2).all()
    if option_filter == "all":
        todos = todos.filter(TodoModel.todo_state != 3).all()
    if not todos:
        return CommonError.get_error(40000)

    if len(todos) == 0:
        return CommonError.error_toast(msg="没有待办")

    result = []
    for todo in todos:
        result.append({
            "todo_id": todo.todo_id,
            "todo_title": todo.todo_title,
            "todo_state": todo.todo_state
        })
    return response_succ(body=result)


@api.route("todo/undo", methods=["POST"])
@login_require
def undo_todo():
    params = request.values or request.get_json() or {}
    todo_id = params.get("todo_id")
    result = set_todo_state(todo_id, 1)
    if not result:
        return CommonError.get_error(40000)
    return response_succ(body=result)
