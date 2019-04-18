import requests as req
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
    # 查看是否可用
    resp = req.post(source)
    if resp.status_code == 404 or resp.status_code >= 500:
        return CommonError.error_toast("wrong link")
    bind_user_id = g.current_user.id
    
    try:
        query = """
        SELECT * FROM bao_rss WHERE rss_link = '{}';
        """.format(source)
        exists = db.session.execute(query).fetchone()
        rss_id = None
        if exists:
            rss_id = exists.rss_id
        else:
            rss = RssModel(source)
            db.session.add(rss)
            db.session.flush() # flush预提交，等于提交到数据库内存
            rss_id = rss.rss_id
        
        query = """
        SELECT * FROM bao_rss_user WHERE user_id = {} and rss_id = {};
        """.format(bind_user_id, rss_id)
        relation_id = db.session.execute(query).fetchone()
        result = {}
        if relation_id:
            result["rss_id"] = rss_id
        else:
            rss_user_relationship = RssUserModel(bind_user_id, rss_id)
            db.session.add(rss_user_relationship)
            db.session.commit()
            result["rss_id"] = rss_id
        from celery_tasks.tasks import async_parser_feed
        async_parser_feed.delay(source)
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


@api.route('/rss/content/list', methods=['POST'])
@login_require
def rss_content_list():
    params = request.values or request.get_json() or {}
    pages = params.get('pages') or 0
    limit = params.get('limit') or 10
    time_desc = params.get('time_is_desc') or 0 # 0 升序 1 降序
    sql = """
    SELECT * FROM bao_rss_content order by add_time {} limit {} offset {} ;
    """.format('desc' if time_desc else 'asc', limit, pages*limit)
    # sqlalchemy执行sql
    data_query = db.session.execute(sql)
    total = data_query.rowcount
    payload = {}
    payload['total'] = total
    payload['pages'] = pages
    payload['limit'] = limit
    payload['list'] = [{
        'link': item['content_link'],
        'base': item['content_base'],
        'add_time': item['add_time'],
        'title': item['content_title'],
        'id': item['content_id'],
    } for item in data_query.fetchall()]
    return response_succ(body=payload)
