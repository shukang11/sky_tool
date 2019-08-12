import re
import logging
import feedparser
from celery_tasks import db
import pymysql
from sqlalchemy.sql import text
from app.utils import get_unix_time_tuple, get_domain

def parser_feed(feed_url: str) -> any:
    feeds = feedparser.parse(feed_url)
    payload = {}
    if not hasattr(feeds, 'version'):
        return payload
    version = feeds.version
    title = feeds.feed.title if hasattr(feeds.feed, 'title') else '' # rss的标题
    link = feeds.feed.link if hasattr(feeds.feed, 'link') else None  # 链接
    if not link: return None
    
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

def parse_inner(url: str, payload: dict) -> bool:
    if not payload: return False
    if len(payload) == 0: return False
    operator_map = {
        "rss20": parse_rss20,
        "atom10": parse_atom,
        "rss10": parse_rss10,
    }
    operator = operator_map.get(payload["version"]) or parse_rss20
    if not operator:
        return False
    version = payload['version'] if hasattr(payload, 'version') else ''
    title = payload['title'] or '无标题'
    subtitle = payload['subtitle']
    items = payload['items']
    for item in items:
        parsed = operator(item)
        descript = ""
        title = parsed["title"]
        link = parsed["link"]
        timeLocal = get_unix_time_tuple()
        query = """
        INSERT INTO bao_rss_content(content_base, content_link, content_title, content_description, add_time)
        VALUES('{url}', '{link}', '{title}', '{descript}', {time}) on duplicate key update add_time='{time}';
        """.format(url=url, link=link, title=title, descript=text(descript), time=timeLocal)
        db.query(query)
    return True

def parse_rss20(item: dict) -> dict:
    """ 
    知乎订阅解析
    {
        "title": "",
        "title_detail": {"type": "text/plain", "language": null, "base": "https://www.zhihu.com/rss", "value": "《彩虹六号：围攻》咖啡厅关卡探讨空间类型组构"},
        "links": [{"rel": "alternate", "type": "text/html", "href": "http://zhuanlan.zhihu.com/p/75380766?utm_campaign=rss&utm_medium=rss&utm_source=rss&utm_content=title"}]
        "link": "",
        "summary": "<>",
        "summary_detail": {"type": "text/html", "language": null, "base": "https://www.zhihu.com/rss", "value": "<>"},
        "authors": [{"name": "暴走的巫師"}],
        "author": "暴走的巫師", 
        "author_detail": {"name": "暴走的巫師"}, 
        "published": "Thu, 01 Aug 2019 19:30:36 +0800", 
        "published_parsed": 12334323423, 
        "id": "http://zhuanlan.zhihu.com/p/75380766", 
        "guidislink": false
    }
    """
    result = {}
    title: str = item["title"]
    summary: str = item["summary"]
    link: str = item["id"]
    published: str = item["published"]
    result.setdefault("title", title)
    result.setdefault("descript", summary)
    result.setdefault("link", link)
    result.setdefault('published', published)
    return result

def parse_rss10(item: dict) -> dict:
    return parse_rss20(item)

def parse_atom(item: dict) -> dict:
    return parse_rss20(item)