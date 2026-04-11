import json
import urllib.request
import os
import re
from xml.etree import ElementTree as ET

def fetch_36kr_news():
    """Fetch from 36kr RSS"""
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
    """Fetch from Wall Street CN"""
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
    """Fetch from Hacker News top stories"""
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
    """Simple translation map for common tech terms"""
    translations = {
        'Show HN': '\u5c55\u793a',
        'Ask HN': '\u8be2\u95ee',
        'Tell HN': '\u5206\u4eab',
        'Launch HN': '\u53d1\u5e03',
        'Google': '\u8c37\u6b4c',
        'Microsoft': '\u5fae\u8f6f',
        'Apple': '\u82f9\u679c',
        'Amazon': '\u4e9a\u9a6c\u900a',
        'Meta': 'Meta',
        'OpenAI': 'OpenAI',
        'AI': 'AI',
        'LLM': '\u5927\u8bed\u8a00\u6a21\u578b',
        'GPU': 'GPU',
        'CPU': 'CPU',
        'Python': 'Python',
        'JavaScript': 'JavaScript',
        'Rust': 'Rust',
        'Linux': 'Linux',
        'Windows': 'Windows',
        'macOS': 'macOS',
        'Docker': 'Docker',
        'Kubernetes': 'Kubernetes',
        'React': 'React',
        'GitHub': 'GitHub',
        'Git': 'Git',
        'API': 'API',
        'database': '\u6570\u636e\u5e93',
        'server': '\u670d\u52a1\u5668',
        'browser': '\u6d4f\u89c8\u5668',
        'security': '\u5b89\u5168',
        'privacy': '\u9690\u79c1',
        'encryption': '\u52a0\u5bc6',
        'hacking': '\u9ed1\u5ba2',
        'startup': '\u521b\u4e1a\u516c\u53f8',
        'funding': '\u878d\u8d44',
        'acquisition': '\u6536\u8d2d',
        'IPO': 'IPO',
        'programming': '\u7f16\u7a0b',
        'software': '\u8f6f\u4ef6',
        'hardware': '\u786c\u4ef6',
        'algorithm': '\u7b97\u6cd5',
        'machine learning': '\u673a\u5668\u5b66\u4e60',
        'deep learning': '\u6df1\u5ea6\u5b66\u4e60',
        'neural network': '\u795e\u7ecf\u7f51\u7edc',
        'cloud': '\u4e91\u7aef',
        'SaaS': 'SaaS',
        'open source': '\u5f00\u6e90',
    }
    
    # Keep original but add context
    result = title
    for en, cn in translations.items():
        if en in title:
            result = result.replace(en, f"{cn}({en})")
    
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
        tech_news.append({
            'title': translate_title(item['title']),
            'url': item['url'],
            'source': 'Hacker News'
        })
    
    # Build message
    title = "\ud83d\udcca \u6bcf\u65e5\u65b0\u95fb\u5feb\u8baf"
    
    lines = [title, ""]
    
    # Finance section
    if finance_news:
        lines.append("\ud83d\udcc8 \u8d22\u7ecf\u65b0\u95fb")  # 璐㈢粡鏂伴椈
        for i, item in enumerate(finance_news, 1):
            lines.append(f"{i}. {item['title']}")
            lines.append(f"   \ud83d\udd17 {item['url']}")
        lines.append("")
    
    # Tech section
    if tech_news:
        lines.append("\ud83d\udcbb \u56fd\u9645\u79d1\u6280")  # 鍥介檯绉戞妧
        for i, item in enumerate(tech_news, 1):
            lines.append(f"{i}. {item['title']}")
            lines.append(f"   \ud83d\udd17 {item['url']}")
        lines.append("")
    
    if not finance_news and not tech_news:
        lines.append("\u6682\u65e0\u65b0\u95fb\u6570\u636e")  # 鏆傛棤鏂伴椈鏁版嵁
    
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
