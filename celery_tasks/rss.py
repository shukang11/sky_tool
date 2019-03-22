import re
import feedparser
from celery_tasks import db
import pymysql
from app.utils import get_unix_time_tuple

def parser_feed(feed_url: str):
    feeds = feedparser.parse(feed_url)
    payload = {}

    version = feeds.version
    title = feeds.feed.title # rss的标题
    link = feeds.feed.link # 链接

    payload['version'] = version
    payload['title'] = title
    payload['link'] = link
    subtitle = None
    if version == 'atom10':
        subtitle = ''
    elif version == 'rss20':
        subtitle = feeds.feed.subtitle or '' # 子标题
    payload['subtitle'] = subtitle

    result = []
    for item in feeds['entries']:
        r = {}
        for k in item:
            r[k] = item[k]
        result.append(r)
    payload['items'] = result
    return payload

def parse_inner(url: str, payload: dict):
    version = payload['version']
    title = payload['title']
    link = payload['link']
    subtitle = payload['subtitle']
    items = payload['items']
    for item in items:
        query = """
        INSERT IGNORE INTO bao_rss_content(content_base, content_link, content_title, content_description, add_time)
        VALUES('{0}', '{1}', '{2}', '{3}', {4}) on duplicate key update add_time='{5}';
        """.format(url, item['link'], item['title'], pymysql.escape_string(item['summary']), get_unix_time_tuple(), get_unix_time_tuple())
        db.query(query)