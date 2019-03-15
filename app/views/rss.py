from flask import request
from celery import Task
from ..views import api
from app.utils import response_succ, CommonError, get_unix_time_tuple, login_require
from app.utils.ext import g, db
from app.models import RssModel, RssUserModel

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
    try:
        exists = db.session.query(RssModel).filter(RssModel.rss_link == source).first()
        rss_id = None
        if exists:
            rss_id = exists.rss_id
        else:
            rss = RssModel(source)
            db.session.add(rss)
            db.session.flush() # flush预提交，等于提交到数据库内存
            rss_id = rss.rss_id
        
        exists_relation_ship = db.session.query(RssUserModel).filter(RssUserModel.rss_user_id == bind_user_id, RssUserModel.rss_id == rss_id).first()
        result = {}
        if exists_relation_ship:
            result["rss_id"] = rss_id
        else:
            rss_user_relationship = RssUserModel(bind_user_id, rss_id)
            db.session.add(rss_user_relationship)
            db.session.commit()
            result["rss_id"] = rss_id
        return response_succ(body=result)
    except Exception as e:
        db.session.rollback()
        print(e)
        return CommonError.get_error(9999)
    

@api.route("/rss/limit", methods=["POST", "GET"])
@login_require
def list_rss():
    params = request.values or request.get_json() or {}
    all_rss = db.session.query(RssModel).filter(RssModel.rss_id == RssUserModel.rss_id).filter(RssUserModel.user_id == g.current_user.id).all()
    result = []
    if not all_rss:
        return CommonError.error_toast(msg="没有订阅")
    for rss in all_rss:
        result.append({
            "rss_id": rss.rss_id,
            "rss_link": rss.rss_link,
        })
    return response_succ(body=result)


@api.route("/rss/parse", methods=["POST", "GET"])
@login_require
def parser_rss():
    params = request.values or request.get_json() or {}
    source = params.get("source")
    from celery_tasks.tasks import async_parser_feed
    task = async_parser_feed.delay(source)
    result = {}
    result['task_id'] = task.id
    return response_succ(body=result)

@api.route('/rss/parser_backend', methods=['GET', 'POST'])
def task_parser_backend():
    params = request.values or request.get_json() or {}
    status = params.get('status')
    result = params.get('result')
    task_id = params.get('task_id')
    payload = {}
    payload['status'] = status
    payload['result'] = result
    payload['task_id'] = task_id
    payload['trackback'] = trackback
    return response_succ(body=payload)