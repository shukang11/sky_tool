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
            # 查看是否可用
            resp = req.post(source)
            if resp.status_code == 404 or resp.status_code >= 500:
                return CommonError.error_toast("wrong link")
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
    # params = request.values or request.get_json() or {}
    # all_rss = db.session.query(RssModel).filter(RssModel.rss_id == RssUserModel.rss_id).filter(RssUserModel.user_id == g.current_user.id).all()
    # result = []
    # if not all_rss:
    #     return CommonError.error_toast(msg="没有订阅")
    # for rss in all_rss:
    #     result.append({
    #         "rss_id": rss.rss_id,
    #         "rss_link": rss.rss_link,
    #     })
    """ rss_base list, query from bao_rss """
    params = request.values or request.get_json() or {}
    bind_user_id = g.current_user.id
    # pages 
    pages = params.get('pages') or 0
    limit = params.get('limit') or 10
    sql = ''
    sql += """
    SELECT bao_rss.rss_id, bao_rss.rss_link, bao_rss.add_time FROM bao_rss
    WHERE bao_rss.rss_id IN (
    SELECT rss_id FROM bao_rss_user WHERE bao_rss_user.user_id={user_id}
    )
    ORDER BY add_time DESC LIMIT {limit} OFFSET {offset};
    """.format(user_id=bind_user_id, limit=limit, offset=pages*limit)
    # sqlalchemy执行sql
    data_query = db.session.execute(sql)
    total = data_query.rowcount
    payload = {}
    payload['total'] = total
    payload['pages'] = pages
    payload['limit'] = limit
    payload['list'] = [{
        'link': item['rss_link'],
        'add_time': item['add_time'],
        'id': item['rss_id'],
    } for item in data_query.fetchall()]
    return response_succ(body=payload)


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


# 获得 bao_rss_content 列表的接口(将废弃)
@api.route('/rss/content/list', methods=['POST'])
@login_require
def rss_content_list():
    params = request.values or request.get_json() or {}
    pages = int(params.get('pages') or 0)
    limit = int(params.get('limit') or 10)
    time_desc = bool(params.get('time_is_desc') or 0) # 0 升序 1 降序
    bind_user_id = g.current_user.id
    sql = """
    SELECT * FROM bao_rss_content
    WHERE bao_rss_content.content_base IN (
        SELECT bao_rss.rss_link
        FROM bao_rss
        WHERE bao_rss.rss_id IN (
            SELECT rss_id FROM bao_rss_user WHERE bao_rss_user.user_id={user_id}
        )
    )
    ORDER BY add_time {order} limit {limit} offset {offset};
    """.format(order='DESC' if time_desc else 'ASC', limit=limit, offset=pages*limit, user_id=bind_user_id)
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


@api.route('/rss/content/filter', methods=['POST'])
@login_require
def rss_content_filter():
    """ 
    filter rss content
    Args:
    bases: list, rss_ids
    pages: -
    limit: -
    tags: not yet
    key_words: not yet
    """
    params = request.values or request.get_json() or {}
    bind_user_id = g.current_user.id
    # 添加根据 base 的 filter
    base = params.get('bases') or []
    # pages 
    pages = params.get('pages') or 0
    limit = params.get('limit') or 10

    # tag 
    tags = params.get('tags') or []

    # key words
    key_words = params.get('key_word') or ''

    sql = ''
    sql += 'SELECT * '
    sql += 'FROM bao_rss_content, bao_rss, bao_rss_user '
    sql += 'ORDER BY add_time {} LIMIT {} OFFSET {} ;'.format('desc' if time_desc else 'asc', limit, pages*limit)

    pass