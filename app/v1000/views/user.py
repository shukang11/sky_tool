
from flask import request, current_app, g
from ..views import api
from app.utils import response_succ, CommonError, UserError
from app.utils import login_require, getmd5, get_random_num
from app.models import User, db


def login():
    pass


@api.route("/user/register", methods=["POST"])
def register():
    params = request.values or request.get_json() or {}
    email = params.get("email")
    password = params.get("password")
    if len(password) != 32:
        return CommonError.get_error(40000)
    exsist_user = db.session.query(User).filter_by(email=email).first()
    if exsist_user:
        return UserError.get_error(40200)
    salt = current_app.config['SECURITY_PASSWORD_SALT'] or 'token'
    token = getmd5("{}{}{}".format(salt, email, get_random_num(5)))
    user = User(email=email, password=password, status=1)
    user.token = token
    db.session.add(user)
    db.session.commit()
    return response_succ(body={"user_id": user.id})


@api.route("/user/login", methods=["POST"])
def login():
    params = request.values or request.get_json() or {}
    email = params.get("email")
    password = params.get("password")
    exsist_user = db.session.query(User).filter_by(email=email, password=password).first()
    if exsist_user:
        # update token
        salt = current_app.config['SECURITY_PASSWORD_SALT'] or 'token'
        token = getmd5("{}{}{}".format(salt, email, get_random_num(5)))
        exsist_user.token = token
        db.session.commit(exsist_user)
        return response_succ()
    else:
        return UserError.get_error(40201)


@api.route("/user/info", methods=["POST"])
@login_require
def user_info():
    user: User = g.current_user
    info = {
        "nickname": user.nickname or "",
        "email": user.email,
        "token": user.token
    }
    return response_succ(body=info)

@api.route("/user/nickname", methods=["GET", "POST"])
@login_require
def set_nickname():
    user: User = g.current_user
    params = request.values
    if request.method == "GET":
        return response_succ(body={"nickname": user.nickname or ""})

    new_name = params.get("nickname")
    user.nickname = new_name
    db.session.commit()
    return user_info()