import json
import urllib.request
import os
import re
from xml.etree import ElementTree as ET

# 低价值关键词过滤（公告、招聘、活动等非新闻内容）
LOW_VALUE_KEYWORDS = [
    '招聘', '诚聘', '加入我们', '活动预告', '报名', '邀请函',
    '公告', '通知', '免责声明', '版权声明', '转载',
    '财报', '年报', '季报', '业绩快报', '停牌', '复牌',
    '增持', '减持', '质押', '解禁', '分红', '派息'
]

def is_low_value(title):
    """判断是否为低价值内容"""
    if not title:
        return True
    title_lower = title.lower()
    for keyword in LOW_VALUE_KEYWORDS:
        if keyword in title:
            return True
    return False

def fetch_36kr_news():
    """获取36氪热门新闻"""
    try:
        url = "https://www.36kr.com/feed-newsflash"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
        root = ET.fromstring(content)
        items = root.findall('.//item')
        news_list = []
        for item in items:
            title_elem = item.find('title')
            link_elem = item.find('link')
            desc_elem = item.find('description')
            if title_elem is not None and link_elem is not None:
                title = title_elem.text or ""
                link = link_elem.text or ""
                # 过滤低价值内容
                if title and link and not is_low_value(title):
                    news_list.append({
                        'title': title, 
                        'url': link, 
                        'source': '36氪'
                    })
                if len(news_list) >= 5:
                    break
        return news_list
    except Exception as e:
        print(f"36kr error: {e}")
        return []

def fetch_wsc_news():
    """获取华尔街见闻热门新闻"""
    try:
        url = "https://api-one.wallstcn.com/apiv1/content/information-flow?channel=global&accept=article&limit=20"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        news_list = []
        items = data.get('data', {}).get('items', [])
        for item in items:
            content = item.get('content', {})
            title = content.get('title', '')
            uri = content.get('uri', '')
            # 过滤低价值内容
            if title and uri and not is_low_value(title):
                news_list.append({
                    'title': title, 
                    'url': uri, 
                    'source': '华尔街见闻'
                })
            if len(news_list) >= 5:
                break
        return news_list
    except Exception as e:
        print(f"WSC error: {e}")
        return []

def fetch_hn_news():
    """获取Hacker News热门新闻（按分数排序取前5）"""
    try:
        # 获取top stories（约500个ID）
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            story_ids = json.loads(response.read().decode('utf-8'))
        
        # 获取前10个story的详细信息（包括分数）
        stories = []
        for story_id in story_ids[:10]:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                req = urllib.request.Request(story_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    story = json.loads(response.read().decode('utf-8'))
                
                title = story.get('title', '')
                url = story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                score = story.get('score', 0)
                
                # 过滤掉招聘帖、Show HN等
                if title and not title.startswith('Ask HN:') and not title.startswith('Show HN:') and not title.startswith('Tell HN:'):
                    stories.append({
                        'title': title,
                        'url': url,
                        'score': score,
                        'id': story_id
                    })
            except:
                continue
        
        # 按分数排序，取前5
        stories.sort(key=lambda x: x['score'], reverse=True)
        
        news_list = []
        for story in stories[:5]:
            news_list.append({
                'title': story['title'],
                'url': story['url'],
                'source': 'Hacker News',
                'score': story['score']
            })
        
        return news_list
    except Exception as e:
        print(f"HN error: {e}")
        return []

def fetch_npr_news():
    """获取NPR国际新闻"""
    try:
        url = "https://feeds.npr.org/1001/rss.xml"
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
                    news_list.append({
                        'title': title,
                        'url': link,
                        'source': 'NPR'
                    })
        return news_list
    except Exception as e:
        print(f"NPR error: {e}")
        return []

def fetch_reuters_news():
    """获取Reuters国际新闻"""
    try:
        url = "https://www.reutersagency.com/feed/?taxonomy=markets&post_type=reuters-best"
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
                    news_list.append({
                        'title': title,
                        'url': link,
                        'source': 'Reuters'
                    })
        return news_list
    except Exception as e:
        print(f"Reuters error: {e}")
        return []

def translate_title(title):
    """翻译Hacker News标题中的常见术语"""
    # 术语映射表
    term_map = {
        r'\bGoogle\b': '谷歌',
        r'\bMicrosoft\b': '微软',
        r'\bApple\b': '苹果',
        r'\bAmazon\b': '亚马逊',
        r'\bMeta\b': 'Meta',
        r'\bOpenAI\b': 'OpenAI',
        r'\bChatGPT\b': 'ChatGPT',
        r'\bLLM\b': '大语言模型',
        r'\bAI\b': 'AI',
        r'\bGPU\b': 'GPU',
        r'\bPython\b': 'Python',
        r'\bJavaScript\b': 'JavaScript',
        r'\bRust\b': 'Rust',
        r'\bLinux\b': 'Linux',
        r'\bWindows\b': 'Windows',
        r'\bGitHub\b': 'GitHub',
        r'\bdatabase\b': '数据库',
        r'\bserver\b': '服务器',
        r'\bsecurity\b': '安全',
        r'\bprivacy\b': '隐私',
        r'\bstartup\b': '创业公司',
        r'\bprogramming\b': '编程',
        r'\bsoftware\b': '软件',
        r'\balgorithm\b': '算法',
        r'\bmachine learning\b': '机器学习',
        r'\bcloud\b': '云',
        r'\bopen source\b': '开源',
        r'\brelease\b': '发布',
        r'\bannounces\b': '宣布',
        r'\blaunches\b': '推出',
        r'\bintroduces\b': '引入',
    }
    
    result = title
    for pattern, replacement in term_map.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result

def remove_duplicates(news_list):
    """去重：相同标题只保留一条"""
    seen = set()
    unique = []
    for item in news_list:
        # 用标题前20个字符作为去重key
        key = item['title'][:20].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

def main():
    print("Fetching news from all sources...")
    
    # 获取各源新闻
    news_36kr = fetch_36kr_news()
    print(f"36氪: {len(news_36kr)}条")
    
    news_wsc = fetch_wsc_news()
    print(f"华尔街见闻: {len(news_wsc)}条")
    
    news_hn = fetch_hn_news()
    print(f"Hacker News: {len(news_hn)}条")
    
    news_npr = fetch_npr_news()
    print(f"NPR: {len(news_npr)}条")
    
    news_reuters = fetch_reuters_news()
    print(f"Reuters: {len(news_reuters)}条")
    
    # 合并财经新闻并去重
    finance_news = remove_duplicates(news_36kr + news_wsc)
    # 取前5条
    finance_news = finance_news[:5]
    
    # 国际热点新闻（NPR + Reuters + HN）- 混合排序取前5
    world_news_raw = news_npr + news_reuters
    # HN 的科技新闻也混入国际板块（因为HN主要是美国科技圈热点）
    for item in news_hn[:3]:
        world_news_raw.append({
            'title': translate_title(item['title']),
            'url': item['url'],
            'source': 'Hacker News'
        })
    
    # 去重后取前5条
    world_news = remove_duplicates(world_news_raw)[:5]
    
    # 构建消息
    title = "📊 每日新闻速递"
    lines = [title, ""]
    
    # 财经板块
    if finance_news:
        lines.append("📈 财经热点")
        for i, item in enumerate(finance_news, 1):
            lines.append(f"{i}. {item['title']}")
            lines.append(f"   🔗 {item['url']}")
        lines.append("")
    
    # 国际热点板块
    if world_news:
        lines.append("🌍 国际热点")
        for i, item in enumerate(world_news, 1):
            lines.append(f"{i}. {item['title']}")
            lines.append(f"   🔗 {item['url']}")
        lines.append("")
    
    if not finance_news and not world_news:
        lines.append("暂无新闻数据")
    
    message = "\n".join(lines)
    
    # 打印预览
    print("\n=== 消息预览 ===")
    print(message[:500] + "..." if len(message) > 500 else message)
    
    # 发送到飞书
    payload = {
        "msg_type": "text",
        "content": {"text": message}
    }
    
    webhook = os.environ['FEISHU_WEBHOOK']
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    
    req = urllib.request.Request(
        webhook,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(req) as response:
        result = response.read().decode()
        print(f"\n飞书响应: {result}")

if __name__ == "__main__":
    main()
