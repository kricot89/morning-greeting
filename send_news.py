import json
import urllib.request
import os
import re
from xml.etree import ElementTree as ET

def fetch_36kr_news():
    try:
        url = "https://www.36kr.com/feed-newsflash"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
        root = ET.fromstring(content)
        items = root.findall('.//item')
        news_list = []
        for item in items[:5]:
            title_elem = item.find('title')
            link_elem = item.find('link')
            if title_elem is not None and link_elem is not None:
                title = title_elem.text or ""
                link = link_elem.text or ""
                if title and link:
                    news_list.append({'title': title, 'url': link, 'source': '36\u6c2a'})
        return news_list
    except Exception as e:
        print(f"36kr error: {e}")
        return []

def fetch_wsc_news():
    try:
        url = "https://api-one.wallstcn.com/apiv1/content/information-flow?channel=global&accept=article&limit=10"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        news_list = []
        items = data.get('data', {}).get('items', [])
        for item in items[:5]:
            content = item.get('content', {})
            title = content.get('title', '')
            uri = content.get('uri', '')
            if title and uri:
                news_list.append({'title': title, 'url': uri, 'source': '\u534e\u5c14\u8857\u89c1\u95fb'})
        return news_list
    except Exception as e:
        print(f"WSC error: {e}")
        return []

def fetch_hn_news():
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            story_ids = json.loads(response.read().decode('utf-8'))
        news_list = []
        for story_id in story_ids[:5]:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                req = urllib.request.Request(story_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    story = json.loads(response.read().decode('utf-8'))
                title = story.get('title', '')
                url = story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                if title:
                    news_list.append({'title': title, 'url': url, 'source': 'Hacker News', 'id': story_id})
            except:
                continue
        return news_list
    except Exception as e:
        print(f"HN error: {e}")
        return []

def translate_title(title):
    """Translate common tech terms in HN titles"""
    # Simple string replacements (case insensitive via lower())
    lower_title = title.lower()
    
    # Build translation map
    trans_map = [
        ('google', '\u8c37\u6b4c'),
        ('microsoft', '\u5fae\u8f6f'),
        ('apple', '\u82f9\u679c'),
        ('amazon', '\u4e9a\u9a6c\u900a'),
        ('meta', 'Meta'),
        ('openai', 'OpenAI'),
        ('chatgpt', 'ChatGPT'),
        ('llm', '\u5927\u8bed\u8a00\u6a21\u578b'),
        ('ai ', 'AI '),
        ('gpu', 'GPU'),
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('rust', 'Rust'),
        ('linux', 'Linux'),
        ('windows', 'Windows'),
        ('github', 'GitHub'),
        ('database', '\u6570\u636e\u5e93'),
        ('server', '\u670d\u52a1\u5668'),
        ('security', '\u5b89\u5168'),
        ('privacy', '\u9690\u79c1'),
        ('startup', '\u521b\u4e1a\u516c\u53f8'),
        ('programming', '\u7f16\u7a0b'),
        ('software', '\u8f6f\u4ef6'),
        ('algorithm', '\u7b97\u6cd5'),
        ('machine learning', '\u673a\u5668\u5b66\u4e60'),
        ('cloud', '\u4e91\u7aef'),
        ('open source', '\u5f00\u6e90'),
    ]
    
    result = title
    for en, cn in trans_map:
        # Case insensitive replace
        pattern = re.compile(re.escape(en), re.IGNORECASE)
        result = pattern.sub(f"{cn}({en})", result)
    
    return result

def main():
    # Fetch from all sources
    news_36kr = fetch_36kr_news()
    news_wsc = fetch_wsc_news()
    news_hn = fetch_hn_news()
    
    # Prepare finance news (36kr + WSC) - take up to 5
    finance_news = []
    finance_news.extend(news_36kr[:3])
    finance_news.extend(news_wsc[:3])
    finance_news = finance_news[:5]
    
    # Prepare tech news (HN) - take up to 5, translate titles
    tech_news = []
    for item in news_hn[:5]:
        translated = translate_title(item['title'])
        tech_news.append({
            'title': translated,
            'url': item['url'],
            'source': 'Hacker News'
        })
    
    # Build message
    title = "\ud83d\udcca \u6bcf\u65e5\u65b0\u95fb\u5feb\u8baf"
    
    lines = [title, ""]
    
    # Finance section
    if finance_news:
        lines.append("\ud83d\udcc8 \u8d22\u7ecf\u65b0\u95fb")
        for i, item in enumerate(finance_news, 1):
            lines.append(f"{i}. {item['title']}")
            lines.append(f"   \ud83d\udd17 {item['url']}")
        lines.append("")
    
    # Tech section
    if tech_news:
        lines.append("\ud83d\udcbb \u56fd\u9645\u79d1\u6280")
        for i, item in enumerate(tech_news, 1):
            lines.append(f"{i}. {item['title']}")
            lines.append(f"   \ud83d\udd17 {item['url']}")
        lines.append("")
    
    if not finance_news and not tech_news:
        lines.append("\u6682\u65e0\u65b0\u95fb\u6570\u636e")
    
    message = "\n".join(lines)
    
    payload = {
        "msg_type": "text",
        "content": {"text": message}
    }
    
    webhook = os.environ['FEISHU_WEBHOOK']
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(
        webhook,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())

if __name__ == "__main__":
    main()
