import json, re, html, os, pathlib, datetime, calendar
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
import requests, feedparser

ROOT=pathlib.Path(__file__).parent
SITE=ROOT/'site'; ARCHIVE=ROOT/'archive'
SITE.mkdir(exist_ok=True); ARCHIVE.mkdir(exist_ok=True)
NOW=datetime.datetime.now(datetime.timezone.utc)
LOCAL=NOW.astimezone(ZoneInfo('Europe/Prague'))
DATE=LOCAL.date().isoformat()
SOURCES=json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
KEYWORDS={'Gaming':['minecraft','nintendo','switch','playstation','ps5','gaming','game','xbox','steam','pokémon','pokemon'], 'Technologie':['artificial intelligence','openai','android','google','ai ','chip','smartphone','technology'], 'Investice':['stock','market','bitcoin','crypto','etf','nasdaq','shares','inflation','economy']}

def clean(s):
    s=re.sub(r'<[^>]+>',' ',s or '')
    return html.unescape(re.sub(r'\s+',' ',s)).strip()

def safe_url(u):
    return u if urlparse(u).scheme in ('https','http') else '#'

def fetch(source):
    try:
        response=requests.get(source['url'],timeout=15,headers={'User-Agent':'MorningBriefRSS/1.0 (+personal news reader)'})
        response.raise_for_status()
        feed=feedparser.parse(response.content)
        out=[]
        for entry in feed.entries[:25]:
            link=safe_url(entry.get('link',''))
            if link=='#': continue
            stamp=entry.get('published_parsed') or entry.get('updated_parsed')
            published=datetime.datetime.fromtimestamp(calendar.timegm(stamp),datetime.timezone.utc) if stamp else None
            age=(NOW-published).total_seconds()/3600 if published else 999
            if age < -3 or age > 72: continue
            title=clean(entry.get('title',''))
            summary=clean(entry.get('summary','') or entry.get('description',''))[:320]
            if not title: continue
            text=(title+' '+summary).lower()
            category=source['category']
            score=max(0,48-age)/4 + sum(4 for kw in KEYWORDS.get(category,[]) if kw in text)
            if category=='Gaming' and any(x in text for x in ['minecraft','nintendo','switch','playstation']):score+=8
            if category=='Technologie' and any(x in text for x in ['openai','android',' ai ','artificial intelligence']):score+=6
            if category=='Investice' and any(x in text for x in ['bitcoin','etf','stock','nasdaq']):score+=5
            out.append(dict(title=title,summary=summary,link=link,source=source['name'],category=category,published=published.isoformat() if published else None,score=score))
        return out
    except Exception as exc:
        print(f"Feed unavailable: {source['name']}: {exc}")
        return []

items=[item for source in SOURCES for item in fetch(source)]
unique={}
for item in sorted(items,key=lambda i:i['score'],reverse=True):
    key=re.sub(r'\W+','',item['title'].lower())[:85]
    if key not in unique:unique[key]=item
items=list(unique.values())
selected=[]
for cat in ['Gaming','Technologie','Investice','Česko a svět']:
    match=next((x for x in items if x['category']==cat and x not in selected),None)
    if match:selected.append(match)
for item in items:
    if len(selected)>=5:break
    if item not in selected:selected.append(item)
if not selected:
    # Preserve previous issue if all sources are unavailable.
    if (SITE/'data.json').exists():
        print('All sources unavailable; preserving existing issue')
        raise SystemExit(0)
    selected=[]

payload={'date':DATE,'updated_at':LOCAL.isoformat(),'timezone':'Europe/Prague','method':'Automatický výběr z RSS; souhrny pocházejí ze zdrojových kanálů.','articles':selected,'source_count':len(SOURCES),'feed_items':len(items)}
(SITE/'data.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
(ARCHIVE/f'{DATE}.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
archive_index=sorted((p.name for p in ARCHIVE.glob('????-??-??.json')),reverse=True)[:90]
(SITE/'archive').mkdir(exist_ok=True)
for p in ARCHIVE.glob('????-??-??.json'):
    if p.name in archive_index:(SITE/'archive'/p.name).write_bytes(p.read_bytes())
(SITE/'archive-index.json').write_text(json.dumps(archive_index),encoding='utf-8')
print(f'Generated {DATE}: {len(selected)} stories from {len(items)} feed entries')
