import re
import feedparser

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
