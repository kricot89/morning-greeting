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
    """Translate common tech terms in HN titles - case insensitive"""
    translations = {
        r'\bShow HN\b': '\u5c55\u793a(Show HN)',
        r'\bAsk HN\b': '\u8be2\u95ee(Ask HN)',
        r'\bTell HN\b': '\u5206\u4eab(Tell HN)',
        r'\bLaunch HN\b': '\u53d1\u5e03(Launch HN)',
        r'\bGoogle\b': '\u8c37\u6b4c(Google)',
        r'\bMicrosoft\b': '\u5fae\u8f6f(Microsoft)',
        r'\bApple\b': '\u82f9\u679c(Apple)',
        r'\bAmazon\b': '\u4e9a\u9a6c\u900a(Amazon)',
        r'\bMeta\b': 'Meta',
        r'\bOpenAI\b': 'OpenAI',
        r'\bChatGPT\b': 'ChatGPT',
        r'\bGPT\b': 'GPT',
        r'\bAI\b': 'AI',
        r'\bLLM\b': '\u5927\u8bed\u8a00\u6a21\u578b(LLM)',
        r'\bGPU\b': 'GPU',
        r'\bCPU\b': 'CPU',
        r'\bPython\b': 'Python',
        r'\bJavaScript\b': 'JavaScript',
        r'\bTypeScript\b': 'TypeScript',
        r'\bRust\b': 'Rust',
        r'\bGo\b': 'Go\u8bed\u8a00',
        r'\bLinux\b': 'Linux',
        r'\bWindows\b': 'Windows',
        r'\bmacOS\b': 'macOS',
        r'\bDocker\b': 'Docker',
        r'\bKubernetes\b': 'Kubernetes(K8s)',
        r'\bReact\b': 'React',
        r'\bVue\b': 'Vue',
        r'\bGitHub\b': 'GitHub',
        r'\bGit\b': 'Git',
        r'\bAPI\b': 'API',
        r'\bCSS\b': 'CSS',
        r'\bHTML\b': 'HTML',
        r'\bSQL\b': 'SQL',
        r'\bJSON\b': 'JSON',
        r'\bHTTP\b': 'HTTP',
        r'\bHTTPS\b': 'HTTPS',
        r'\bURL\b': '\u7f51\u5740',
        r'\bdatabase\b': '\u6570\u636e\u5e93(database)',
        r'\bserver\b': '\u670d\u52a1\u5668(server)',
        r'\bbrowser\b': '\u6d4f\u89c8\u5668(browser)',
        r'\bsecurity\b': '\u5b89\u5168(security)',
        r'\bprivacy\b': '\u9690\u79c1(privacy)',
        r'\bencryption\b': '\u52a0\u5bc6(encryption)',
        r'\bhacking\b': '\u9ed1\u5ba2(hacking)',
        r'\bhacker\b': '\u9ed1\u5ba2(hacker)',
        r'\bstartup\b': '\u521b\u4e1a\u516c\u53f8(startup)',
        r'\bfunding\b': '\u878d\u8d44(funding)',
        r'\bacquisition\b': '\u6536\u8d2d(acquisition)',
        r'\bIPO\b': 'IPO',
        r'\bprogramming\b': '\u7f16\u7a0b(programming)',
        r'\bsoftware\b': '\u8f6f\u4ef6(software)',
        r'\bhardware\b': '\u786c\u4ef6(hardware)',
        r'\balgorithm\b': '\u7b97\u6cd5(algorithm)',
        r'\bmachine learning\b': '\u673a\u5668\u5b66\u4e60(ML)',
        r'\bdeep learning\b': '\u6df1\u5ea6\u5b66\u4e60(DL)',
        r'\bneural network\b': '\u795e\u7ecf\u7f51\u7edc(NN)',
        r'\bcloud\b': '\u4e91\u7aef(cloud)',
        r'\bSaaS\b': 'SaaS',
        r'\bopen source\b': '\u5f00\u6e90(open source)',
        r'\bfirmware\b': '\u56fa\u4ef6(firmware)',
        r'\bdriver\b': '\u9a71\u52a8(driver)',
        r'\bkernel\b': '\u5185\u6838(kernel)',
        r'\bbug\b': 'Bug',
        r'\bdebug\b': '\u8c03\u8bd5(debug)',
        r'\brelease\b': '\u53d1\u5e03(release)',
        r'\bupdate\b': '\u66f4\u65b0(update)',
        r'\bversion\b': '\u7248\u672c(version)',
        r'\bdeprecated\b': '\u5df2\u5f03\u7528(deprecated)',
        r'\bvulnerability\b': '\u6f0f\u6d1e(vulnerability)',
        r'\bexploit\b': '\u6f0f\u6d1e\u5229\u7528(exploit)',
        r'\bmalware\b': '\u6076\u610f\u8f6f\u4ef6(malware)',
        r'\bvirus\b': '\u75c5\u6bd2(virus)',
        r'\bphishing\b': '\u7f51\u7edc\u9493\u9c7c(phishing)',
        r'\b2FA\b': '\u4e8c\u6b21\u9a8c\u8bc1(2FA)',
        r'\bMFA\b': '\u591a\u91cd\u9a8c\u8bc1(MFA)',
        r'\bOAuth\b': 'OAuth',
        r'\bJWT\b': 'JWT',
        r'\bSSL\b': 'SSL',
        r'\bTLS\b': 'TLS',
        r'\bVPN\b': 'VPN',
        r'\bproxy\b': '\u4ee3\u7406(proxy)',
        r'\bcache\b': '\u7f13\u5b58(cache)',
        r'\bCDN\b': 'CDN',
        r'\bload balancer\b': '\u8d1f\u8f7d\u5747\u8861',
        r'\bmicroservice\b': '\u5fae\u670d\u52a1',
        r'\bcontainer\b': '\u5bb9\u5668(container)',
        r'\bvirtual machine\b': '\u865a\u62df\u673a(VM)',
        r'\bVM\b': 'VM',
        r'\bbackend\b': '\u540e\u7aef(backend)',
        r'\bfrontend\b': '\u524d\u7aef(frontend)',
        r'\bfull-stack\b': '\u5168\u6808(full-stack)',
        r'\bdevops\b': 'DevOps',
        r'\bCI/CD\b': 'CI/CD',
        r'\btest\b': '\u6d4b\u8bd5(test)',
        r'\bbenchmark\b': '\u6027\u80fd\u6d4b\u8bd5(benchmark)',
        r'\bperformance\b': '\u6027\u80fd(performance)',
        r'\boptimize\b': '\u4f18\u5316(optimize)',
        r'\brefactor\b': '\u91cd\u6784(refactor)',
        r'\blegacy\b': '\u9057\u7559(legacy)',
        r'\bmonolith\b': '\u5355\u4f53\u67b6\u6784',
        r'\bdistributed\b': '\u5206\u5e03\u5f0f',
        r'\bscalable\b': '\u53ef\u6269\u5c55\u7684',
        r'\bconcurrent\b': '\u5e76\u53d1',
        r'\bparallel\b': '\u5e76\u884c',
        r'\basynchronous\b': '\u5f02\u6b65(async)',
        r'\bsynchronous\b': '\u540c\u6b65(sync)',
        r'\bthread\b': '\u7ebf\u7a0b(thread)',
        r'\bprocess\b': '\u8fdb\u7a0b(process)',
        r'\bmemory\b': '\u5185\u5b58(memory)',
        r'\bstorage\b': '\u5b58\u50a8(storage)',
        r'\bdisk\b': '\u78c1\u76d8(disk)',
        r'\bSSD\b': 'SSD',
        r'\bRAM\b': '\u5185\u5b58(RAM)',
        r'\bcompression\b': '\u538b\u7f29(compression)',
        r'\bencode\b': '\u7f16\u7801(encode)',
        r'\bdecode\b': '\u89e3\u7801(decode)',
        r'\bparsing\b': '\u89e3\u6790(parsing)',
        r'\btoken\b': '\u4ee4\u724c(token)',
        r'\bsession\b': '\u4f1a\u8bdd(session)',
        r'\bcookie\b': 'Cookie',
        r'\bwebhook\b': 'Webhook',
        r'\bsocket\b': 'Socket',
        r'\bWebSocket\b': 'WebSocket',
        r'\bREST\b': 'REST',
        r'\bGraphQL\b': 'GraphQL',
        r'\bgRPC\b': 'gRPC',
        r'\bprotobuf\b': 'Protobuf',
        r'\bXML\b': 'XML',
        r'\bYAML\b': 'YAML',
        r'\bTOML\b': 'TOML',
        r'\bregex\b': '\u6b63\u5219\u8868\u8fbe\u5f0f',
        r'\bparser\b': '\u89e3\u6790\u5668',
        r'\bcompiler\b': '\u7f16\u8bd1\u5668',
        r'\binterpreter\b': '\u89e3\u91ca\u5668',
        r'\bruntime\b': '\u8fd0\u884c\u65f6',
        r'\bframework\b': '\u6846\u67b6(framework)',
        r'\blibrary\b': '\u5e93(library)',
        r'\bpackage\b': '\u5305(package)',
        r'\bmodule\b': '\u6a21\u5757(module)',
        r'\bdependency\b': '\u4f9d\u8d56(dependency)',
        r'\bNPM\b': 'NPM',
        r'\bPyPI\b': 'PyPI',
        r'\bMaven\b': 'Maven',
        r'\bGradle\b': 'Gradle',
        r'\bCMake\b': 'CMake',
        r'\bmake\b': 'Make',
        r'\bgit\b': 'Git',
        r'\bcommit\b': '\u63d0\u4ea4(commit)',
        r'\bbranch\b': '\u5206\u652f(branch)',
        r'\bmerge\b': '\u5408\u5e76(merge)',
        r'\brebase\b': '\u53d8\u57fa(rebase)',
        r'\bfork\b': '\u5206\u53c9(fork)',
        r'\bclone\b': '\u514b\u9686(clone)',
        r'\bpull\b': '\u62c9\u53d6(pull)',
        r'\bpush\b': '\u63a8\u9001(push)',
        r'\brepository\b': '\u4ed3\u5e93(repo)',
        r'\bissue\b': '\u95ee\u9898(issue)',
        r'\bPR\b': '\u5408\u5e76\u8bf7\u6c42(PR)',
        r'\bcode review\b': '\u4ee3\u7801\u5ba1\u67e5',
        r'\blint\b': '\u4ee3\u7801\u68c0\u67e5(lint)',
        r'\bformatter\b': '\u4ee3\u7801\u683c\u5f0f\u5316',
        r'\bdocumentation\b': '\u6587\u6863(docs)',
        r'\bREADME\b': 'README',
        r'\bchangelog\b': '\u66f4\u65b0\u65e5\u5fd7',
        r'\blicense\b': '\u6388\u6743\u534f\u8bae',
        r'\bMIT\b': 'MIT',
        r'\bGPL\b': 'GPL',
        r'\bApache\b': 'Apache',
        r'\bBSD\b': 'BSD',
        r'\btrademark\b': '\u5546\u6807',
        r'\bcopyright\b': '\u7248\u6743',
        r'\bpatent\b': '\u4e13\u5229',
    }
    
    result = title
    for pattern, replacement in translations.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
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
