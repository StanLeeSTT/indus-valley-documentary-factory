from __future__ import annotations
import hashlib,json,os,re,subprocess,time
from pathlib import Path
import requests
PROJECT_ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((PROJECT_ROOT/'config/project.json').read_text())

def ensure_dirs():
    for d in ['config','research','media','scenes','narration','subtitles','output','logs','backups','data']:
        (PROJECT_ROOT/d).mkdir(parents=True,exist_ok=True)

def read_json(p,default=None):
    p=Path(p)
    if not p.exists(): return default
    return json.loads(p.read_text(encoding='utf-8'))

def write_json(p,obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')

def norm(v): return re.sub(r'\s+',' ',str(v or '')).strip()

def canonical_key(r):
    doi=norm(r.get('doi')).lower()
    if doi: return 'doi:'+doi
    return 'meta:'+re.sub(r'[^a-z0-9]+','-',(norm(r.get('title'))+'|'+norm(r.get('year'))).lower()).strip('-')

def session():
    s=requests.Session(); s.headers.update({'User-Agent':CONFIG['user_agent'],'Accept-Language':'en-US,en;q=0.8'}); return s
S=session()

def get(url):
    try:
        r=S.get(url,timeout=CONFIG['timeout'],allow_redirects=True)
        return r
    except Exception as e:
        return None

def clean_html(html):
    try:
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(html,'html.parser')
        for x in soup(['script','style','noscript']): x.decompose()
        return norm(soup.get_text(' '))
    except Exception:
        return norm(re.sub('<[^>]+>',' ',html))

def checkpoint(cell,purpose,outputs,stats=None):
    payload={'project_id':CONFIG['project_id'],'cell':cell,'purpose':purpose,'outputs':outputs,'stats':dict(stats or {}),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    write_json(PROJECT_ROOT/f'logs/cell_{cell:02d}_checkpoint.json',payload)
    return payload

def git_checkpoint(cell):
    try:
        subprocess.run(['git','add','.'],cwd=PROJECT_ROOT,check=True,capture_output=True)
        q=subprocess.run(['git','diff','--cached','--quiet'],cwd=PROJECT_ROOT)
        if q.returncode==0: return 'no_changes'
        c=subprocess.run(['git','commit','-m',f'Progress: Cell {cell}'],cwd=PROJECT_ROOT,text=True,capture_output=True)
        if c.returncode!=0: return 'commit_failed: '+c.stderr[-500:]
        p=subprocess.run(['git','push'],cwd=PROJECT_ROOT,text=True,capture_output=True)
        return 'push_ok' if p.returncode==0 else 'push_failed: '+p.stderr[-500:]
    except Exception as e: return 'git_error: '+str(e)
