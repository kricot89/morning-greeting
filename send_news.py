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
    """Fetch from Wall Street CN (\u534e\u5c14\u8857\u89c1\u95fb)"""
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
        # Get top story IDs
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
                    news_list.append({'title': title, 'url': url, 'source': 'Hacker News'})
            except:
                continue
        return news_list
    except Exception as e:
        print(f"HN error: {e}")
        return []

def main():
    # Fetch from all sources
    news_36kr = fetch_36kr_news()
    news_wsc = fetch_wsc_news()
    news_hn = fetch_hn_news()
    
    # Combine all news
    all_news = []
    all_news.extend([n for n in news_36kr])
    all_news.extend([n for n in news_wsc])
    all_news.extend([n for n in news_hn])
    
    # Build message
    title = "\ud83d\udcca \u6bcf\u65e5\u8d22\u7ecf\u5feb\u8baf"
    
    if all_news:
        lines = [title, ""]
        current_source = None
        for i, item in enumerate(all_news[:10], 1):
            # Add source header if changed
            if item['source'] != current_source:
                if current_source is not None:
                    lines.append("")
                source_emoji = "\ud83d\udcc8" if item['source'] == '36\u6c2a' else "\ud83c\udf0f" if item['source'] == '\u534e\u5c14\u8857\u89c1\u95fb' else "\ud83d\udcbb"
                lines.append(f"{source_emoji} {item['source']}")
                current_source = item['source']
            lines.append(f"  {i}. {item['title']}")
        
        message = "\n".join(lines)
    else:
        message = f"{title}\n\n\u6682\u65e0\u65b0\u95fb\u6570\u636e"
    
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
