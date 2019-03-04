from flask import request
from ..views import api
from app.utils import response_succ, CommonError, get_unix_time_tuple, login_require
from app.utils.ext import g, db
from app.models import RssModel

@api.route("/rss/add", methods=["POST"])
@login_require
def add_rss_source():
    """ add a rss
    try add a url to rss list
    """
    params = request.values or request.get_json() or {}
    source = params.get("source")
    if not source:
        return CommonError.get_error(40000)
    bind_user_id = g.current_user.id
    rss = RssModel(source, bind_user_id)
    db.session.add(rss)
    db.session.commit()
    result = {
        "rss_id": rss.rss_id
    }
    return response_succ(body=result)

@api.route("/rss/all", methods=["POST", "GET"])
@login_require
def list_rss():
    params = request.values or request.get_json() or {}
    all_rss = db.session.query(RssModel).filter(
        RssModel.bind_user_id == g.current_user.id).all()
    result = []
    if not all_rss:
        return CommonError.error_toast(msg="没有订阅")
    for rss in all_rss:
        result.append({
            "rss_id": rss.rss_id,
            "rss_link": rss.rss_link,
            "todo_state": rss.rss_state
        })
    return response_succ(body=result)