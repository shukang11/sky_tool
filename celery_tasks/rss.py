import re
import feedparser
from celery_tasks import db
import pymysql
from app.utils import get_unix_time_tuple

def parser_feed(feed_url: str):
    feeds = feedparser.parse(feed_url)
    version = feeds.version
    title = feeds.feed.title # rss的标题
    link = feeds.feed.link # 链接
    subtitle = feeds.feed.subtitle # 子标题
    result = []
    for item in feeds['entries']:
        r = {}
        for k in item:
            r[k] = item[k]
        result.append(r)
    return {
        'version': version,
        'title': title,
        'link': link,
        'subtitle': subtitle,
        'items': result
    }

def parse_inner(url: str, payload: dict):
    version = payload['version']
    title = payload['title']
    link = payload['link']
    subtitle = payload['subtitle']
    items = payload['items']
    if 'zhihu' in url or 'oschina' in url:
        for item in items:
            try:
                query = """
                INSERT INTO bao_rss_content(content_base, content_link, content_title, content_description, add_time)
                VALUES('{0}', '{1}', '{2}', '{3}', {4});
                """.format(url, item['link'], item['title'], pymysql.escape_string(item['summary']), get_unix_time_tuple())
                db.query(query)
            except Exception as e:
                continue