import re
from flask import request
from celery import Task
from ..views import api
from app.utils import response_succ, CommonError, get_unix_time_tuple, login_require, pages_info_require, get_header
from app.utils.ext import g, db
from app.models import RssModel, RssUserModel

@api.route("/rss/add", methods=["POST"])
@login_require
def add_rss_source():
    """ 添加一个订阅源
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
            regex = r'(https?)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]'
            result = re.match(regex, source)
            if not result:
                return  CommonError.error_toast("wrong link")
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
@pages_info_require
def list_rss():
    """ 查看订阅列表 """
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
    """ 开启解析任务 """
    params = request.values or request.get_json() or {}
    source = params.get("source")
    from celery_tasks.tasks import async_parser_feed
    task = async_parser_feed.delay(source)
    result = {}
    result['task_id'] = task.id
    return response_succ(body=result)


@api.route('/rss/parser_backend', methods=['GET', 'POST'])
def task_parser_backend():
    """ 用于接受解析回调，暂时无用 """
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
@pages_info_require
def rss_content_list():
    """ 获取可读内容的列表 """
    params = request.values or request.get_json() or {}
    limit: int
    pages: int
    offset: int
    if g.pageinfo:
        limit = g.pageinfo['limit']
        offset = g.pageinfo['offset']
        pages = g.pageinfo['pages']
    time_desc = bool(params.get('time_is_desc') or 0) # 0 升序 1 降序
    filter_rss_ids = params.get('filter_rss_ids')
    bind_user_id = g.current_user.id

    # query rss_ids
    if filter_rss_ids:
        filter_rss_ids = str(filter_rss_ids).split(',').strip()
        filter_rss_ids = ', '.join(filter_rss_ids)
        sql = """
        SELECT bao_rss_user.rss_id FROM bao_rss_user WHERE bao_rss_user.user_id={user_id} AND bao_rss_user.rss_id IN ( # 筛选选择的rss_id
                {filter}
            );
        """.format(user_id=bind_user_id, filter=filter_rss_ids)
    else: 
        sql = """
        SELECT bao_rss_user.rss_id FROM bao_rss_user WHERE bao_rss_user.user_id={user_id}
        """.format(user_id=bind_user_id)
    data_query = db.session.execute(sql)
    all_rss_ids = [str(item['rss_id']) for item in data_query.fetchall()]
    if len(all_rss_ids) == 0:
        return CommonError.error_toast(msg='no content')
    query_rss_ids = ', '.join(all_rss_ids)

    # 查询 content
    sql = """
    SELECT * FROM bao_rss_content
    WHERE bao_rss_content.content_base IN ( # rss网址
        SELECT bao_rss.rss_link FROM bao_rss  WHERE bao_rss.rss_id IN ( # 筛选当前用户订阅的地址
        {rss_ids}
        )
    )
    ORDER BY add_time {order} limit {limit} offset {offset};
    """.format( rss_ids=query_rss_ids,
                order='DESC' if time_desc else 'ASC', 
                limit=limit, offset=offset, 
                user_id=bind_user_id)
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

@api.route('/rss/record', methods=['GET', 'POST'])
@login_require
def rss_record():
    params = request.values or request.get_json() or {}
    url = str(params.get('url'))
    if not url:
        return CommonError.get_error(40000)
    bind_user_id = g.current_user.id
    sql = """
    SELECT bao_rss_user.user_id, bao_rss.rss_id, bao_rss_content.content_id FROM bao_rss_content, bao_rss, bao_rss_user
    WHERE bao_rss_content.content_link='{content_link}' 
        AND bao_rss_content.content_base=bao_rss.rss_link 
        AND bao_rss.rss_id=bao_rss_user.rss_id 
        AND bao_rss_user.user_id={user_id};
    """.format(content_link=url, user_id=bind_user_id)
    data_query = db.session.execute(sql).fetchone()
    if not data_query:
        return CommonError.error_toast('no match data')
    sql = """
    INSERT INTO bao_rss_read_record(read_url_id, read_user_id, read_time) VALUES ({read_url_id}, {read_user_id}, '{read_time}');
    """.format(read_url_id=data_query['content_id'], read_user_id=data_query['user_id'], read_time=get_unix_time_tuple())
    data_query = db.session.execute(sql)
    db.session.commit()
    return response_succ(body={'state': 'success'})    