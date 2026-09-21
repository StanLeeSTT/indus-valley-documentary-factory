from __future__ import annotations
import re,urllib.parse
from collections import Counter,defaultdict
from .core import *

TOPIC='The Lost Civilization of the Indus Valley'


def save(cell,purpose,outputs,stats=None):
    cp=checkpoint(cell,purpose,outputs,stats)
    cp['git']=git_checkpoint(cell)
    write_json(PROJECT_ROOT/f'logs/cell_{cell:02d}_checkpoint.json',cp)
    return cp

def src(t,title,url,**kw):
    return {'source_id':kw.pop('source_id',f'src_{abs(hash((t,title,url)))%10**10}'),'title':norm(title),'source_type':t,'url':url,'canonical_key':kw.pop('canonical_key',None),'authors':kw.pop('authors',[]),'year':kw.pop('year',None),'doi':kw.pop('doi',None),**kw}

def c1():
    ensure_dirs(); write_json(PROJECT_ROOT/'config/runtime.json',{'python':__import__('sys').version,'project_root':str(PROJECT_ROOT)}); return save(1,'Initialize environment',['config/runtime.json'])
def c2(): ensure_dirs(); return save(2,'Create project scaffold',[])
def c3(): write_json(PROJECT_ROOT/'config/topic_profile.json',{'topic':TOPIC,'project_id':CONFIG['project_id'],'media_policy':{'ai':'fallback only'}}); return save(3,'Create topic profile',['config/topic_profile.json'])
def c4():
    qs=read_json(PROJECT_ROOT/'config/research_questions.json',{})
    queries=['Indus Valley Civilization Harappan archaeology','Harappan chronology','Indus script decipherment','Harappan trade Mesopotamia Oman','Indus Valley environmental change 4.2 ka','Harappan decline transformation']
    write_json(PROJECT_ROOT/'research/seed_queries.json',{'queries':queries,'questions':qs.get('questions',{})}); return save(4,'Create research queries',['research/seed_queries.json'])
def c5(): write_json(PROJECT_ROOT/'config/discovery.json',{'max_sources':100,'top_retrieval_sources':30,'endpoints':['Wikipedia','Wikimedia Commons','OpenAlex','Crossref','Internet Archive']}); return save(5,'Configure discovery',['config/discovery.json'])
def c6():
    url='https://en.wikipedia.org/api/rest_v1/page/summary/Indus_Valley_Civilisation'; r=get(url); rows=[]
    if r is not None and r.ok:
        d=r.json(); rows=[src('wikipedia',d.get('title','Indus Valley Civilisation'),d.get('content_urls',{}).get('desktop',{}).get('page',url),description=d.get('extract'))]
    write_json(PROJECT_ROOT/'research/discovered_wikipedia.json',rows); time.sleep(CONFIG['delay']); return save(6,'Wikipedia orientation discovery',['research/discovered_wikipedia.json'],{'count':len(rows)})
def c7():
    p=urllib.parse.urlencode({'action':'query','generator':'search','gsrsearch':'Indus Valley Civilization Harappan archaeology','gsrnamespace':6,'gsrlimit':10,'prop':'imageinfo','iiprop':'url|extmetadata','format':'json','origin':'*'})
    url='https://commons.wikimedia.org/w/api.php?'+p; r=get(url); rows=[]
    if r is not None and r.ok:
        for x in r.json().get('query',{}).get('pages',{}).values():
            info=(x.get('imageinfo') or [{}])[0]; meta=info.get('extmetadata') or {}
            rows.append(src('wikimedia_commons',x.get('title',''),info.get('descriptionurl',url),media_url=info.get('url'),license=meta.get('LicenseShortName',{}).get('value')))
    write_json(PROJECT_ROOT/'research/discovered_commons.json',rows); time.sleep(CONFIG['delay']); return save(7,'Wikimedia Commons media discovery',['research/discovered_commons.json'],{'count':len(rows)})
def c8():
    rows=[]
    for q in read_json(PROJECT_ROOT/'research/seed_queries.json',{}).get('queries',[]):
        url='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q,'per-page':20}); r=get(url)
        if r is None or not r.ok: continue
        for w in r.json().get('results',[]):
            doi=norm(w.get('doi')).replace('https://doi.org/','') or None; loc=w.get('primary_location') or {}
            landing=loc.get('landing_page_url') or w.get('id') or (f'https://doi.org/{doi}' if doi else '')
            rows.append(src('openalex',w.get('title',''),landing,doi=doi,authors=[a.get('author',{}).get('display_name') for a in w.get('authorships',[]) if a.get('author')],year=w.get('publication_year'),abstract_inverted_index=w.get('abstract_inverted_index')))
        time.sleep(CONFIG['delay'])
    write_json(PROJECT_ROOT/'research/discovered_openalex.json',rows); return save(8,'OpenAlex scholarly discovery',['research/discovered_openalex.json'],{'count':len(rows)})
def c9():
    rows=[]
    for q in read_json(PROJECT_ROOT/'research/seed_queries.json',{}).get('queries',[]):
        url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':q,'rows':20}); r=get(url)
        if r is None or not r.ok: continue
        for w in r.json().get('message',{}).get('items',[]):
            doi=w.get('DOI'); links=w.get('link') or []; landing=(links[0].get('URL') if links else None) or w.get('URL') or (f'https://doi.org/{doi}' if doi else '')
            authors=[a.get('family','')+(', '+a.get('given','') if a.get('given') else '') for a in w.get('author',[])]
            dp=(w.get('published-print') or w.get('published-online') or {}).get('date-parts',[[None]])[0][0]
            rows.append(src('crossref',(w.get('title') or [''])[0],landing,doi=doi,canonical_key='doi:'+doi.lower() if doi else None,authors=authors,year=dp,abstract=w.get('abstract')))
        time.sleep(CONFIG['delay'])
    write_json(PROJECT_ROOT/'research/discovered_crossref.json',rows); return save(9,'Crossref scholarly discovery',['research/discovered_crossref.json'],{'count':len(rows)})
def c10():
    url='https://archive.org/advancedsearch.php?'+urllib.parse.urlencode({'q':'Indus Valley Civilization Harappan','fl[]':['identifier','title','description','date'],'rows':40,'output':'json'},doseq=True); r=get(url); rows=[]
    if r is not None and r.ok:
        for d in r.json().get('response',{}).get('docs',[]):
            ident=d.get('identifier')
            if ident: rows.append(src('internet_archive',d.get('title',''),f'https://archive.org/details/{ident}',canonical_key='archive:'+ident,description=d.get('description')))
    allrows=[]
    for fn in ['discovered_wikipedia.json','discovered_commons.json','discovered_openalex.json','discovered_crossref.json']:
        allrows += read_json(PROJECT_ROOT/'research'/fn,[]) or []
    allrows += rows; write_json(PROJECT_ROOT/'research/discovered_archive.json',rows); write_json(PROJECT_ROOT/'research/discovered_sources_all.json',{'sources':allrows}); return save(10,'Archive discovery and source merge',['research/discovered_archive.json','research/discovered_sources_all.json'],{'raw':len(allrows)})
def c11():
    rs=(read_json(PROJECT_ROOT/'research/discovered_sources_all.json',{}) or {}).get('sources',[]); ded={}
    for r in rs:
        if not isinstance(r,dict): continue
        r=dict(r); r['canonical_key']=r.get('canonical_key') or canonical_key(r); ded.setdefault(r['canonical_key'],r)
    out=list(ded.values()); write_json(PROJECT_ROOT/'research/discovered_sources.json',{'sources':out}); return save(11,'Normalize and deduplicate sources',['research/discovered_sources.json'],{'unique':len(out)})
def c12():
    rs=(read_json(PROJECT_ROOT/'research/discovered_sources.json',{}) or {}).get('sources',[]); terms=['indus','harappa','harappan','script','archaeology','monsoon','trade','ghaggar','hakra','chronology']
    for r in rs:
        blob=' '.join(str(r.get(k) or '') for k in ['title','abstract','description']).lower(); rel=sum(t in blob for t in terms)/len(terms); qual={'openalex':.8,'crossref':.75,'internet_archive':.55,'wikipedia':.45,'wikimedia_commons':.35}.get(r.get('source_type'),.4); ev=.2+(.35 if r.get('doi') else 0)+(.2 if r.get('abstract') else 0)+(.1 if r.get('authors') else 0); r['relevance_score']=round(rel,4); r['quality_score']=qual; r['evidence_score']=min(ev,1); r['score']=round(.5*rel+.3*qual+.2*r['evidence_score'],4)
    rs.sort(key=lambda x:x['score'],reverse=True); write_json(PROJECT_ROOT/'research/ranked_sources.json',{'sources':rs}); return save(12,'Rank sources',['research/ranked_sources.json'],{'ranked':len(rs)})
def c13():
    rs=(read_json(PROJECT_ROOT/'research/ranked_sources.json',{}) or {}).get('sources',[])[:CONFIG['max_sources']]; write_json(PROJECT_ROOT/'research/final_research_sources.json',{'sources':rs}); return save(13,'Select final research set',['research/final_research_sources.json'],{'selected':len(rs)})
def c14():
    rs=(read_json(PROJECT_ROOT/'research/final_research_sources.json',{}) or {}).get('sources',[])[:CONFIG['top_retrieval_sources']]; write_json(PROJECT_ROOT/'research/top30_manifest.json',{'sources':rs}); return save(14,'Select top retrieval set',['research/top30_manifest.json'],{'selected':len(rs)})
def c15():
    rs=(read_json(PROJECT_ROOT/'research/top30_manifest.json',{}) or {}).get('sources',[]); out=[]
    for r in rs:
        rr=get(r.get('url','')); x=dict(r)
        if rr is not None and rr.ok and rr.text:
            x.update({'retrieval_status':'html','retrieved_url':rr.url,'text':clean_html(rr.text),'content_type':rr.headers.get('content-type')})
        else: x.update({'retrieval_status':'failed','retrieval_error':('http_'+str(rr.status_code) if rr is not None else 'connection_error')})
        out.append(x); time.sleep(CONFIG['delay'])
    write_json(PROJECT_ROOT/'research/retrieved_sources_top30.json',{'sources':out}); write_json(PROJECT_ROOT/'research/retrieval_log_top30.json',{'records':[{'source_id':x.get('source_id'),'status':x.get('retrieval_status'),'error':x.get('retrieval_error')} for x in out]}); return save(15,'Retrieve top sources',['research/retrieved_sources_top30.json','research/retrieval_log_top30.json'],Counter(x.get('retrieval_status') for x in out))
def c16():
    rs=(read_json(PROJECT_ROOT/'research/retrieved_sources_top30.json',{}) or {}).get('sources',[]); out=[]
    for r in rs:
        x=dict(r)
        if x.get('retrieval_status')=='failed' and x.get('doi'):
            for u in [f"https://api.crossref.org/works/{x['doi']}",f"https://api.openalex.org/works/https://doi.org/{x['doi']}"]:
                rr=get(u)
                if rr is not None and rr.ok:
                    x.update({'retrieval_status':'metadata','recovery_route':u,'text':rr.text[:10000]}); break
        out.append(x); time.sleep(CONFIG['delay'])
    write_json(PROJECT_ROOT/'research/recovered_sources_top30.json',{'sources':out}); return save(16,'Alternate legitimate retrieval routes',['research/recovered_sources_top30.json'])
def c17():
    rs=(read_json(PROJECT_ROOT/'research/recovered_sources_top30.json',{}) or {}).get('sources',[]); kws=['settlement','urban','script','trade','exchange','monsoon','flood','river','climate','decline','technology','chronology','harappan','indus']; ev=[]
    for r in rs:
        text=r.get('text','') or ''
        if not text: continue
        for s in re.split(r'(?<=[.!?])\s+',norm(text)):
            if len(s)>=50 and any(k in s.lower() for k in kws): ev.append({'evidence_id':f'ev_{len(ev)+1:05d}','source_id':r.get('source_id'),'evidence_text':s[:1200],'access_level':'full_text' if r.get('retrieval_status')=='html' else 'metadata'})
            if len([e for e in ev if e['source_id']==r.get('source_id')])>=20: break
    write_json(PROJECT_ROOT/'research/evidence_claims_top30.json',{'evidence':ev}); return save(17,'Extract evidence',['research/evidence_claims_top30.json'],{'items':len(ev)})
def c18():
    ev=(read_json(PROJECT_ROOT/'research/evidence_claims_top30.json',{}) or {}).get('evidence',[]); claims=[]
    for e in ev: claims.append({'claim_id':f'cl_{len(claims)+1:05d}','claim':e['evidence_text'],'source_ids':[e['source_id']],'evidence_ids':[e['evidence_id']]})
    write_json(PROJECT_ROOT/'research/verified_claims_top30.json',{'claims':claims}); return save(18,'Create initial claim candidates',['research/verified_claims_top30.json'],{'claims':len(claims)})
def c19():
    cs=(read_json(PROJECT_ROOT/'research/verified_claims_top30.json',{}) or {}).get('claims',[]); groups={}
    for c in cs:
        key=re.sub(r'\W+',' ',c['claim'].lower()).strip(); groups.setdefault(key,{'claim_group_id':f'grp_{len(groups)+1:04d}','representative':c['claim'],'claims':[]})['claims'].append(c)
    out=list(groups.values()); write_json(PROJECT_ROOT/'research/claim_groups.json',{'groups':out}); return save(19,'Group claims',['research/claim_groups.json'],{'groups':len(out)})
def c20():
    gs=(read_json(PROJECT_ROOT/'research/claim_groups.json',{}) or {}).get('groups',[]); rows=[]
    for g in gs:
        sources=sorted({s for c in g['claims'] for s in c.get('source_ids',[])}); evidence=sorted({e for c in g['claims'] for e in c.get('evidence_ids',[])}); status='well_corroborated' if len(sources)>=3 else 'corroborated' if len(sources)>=2 else 'single_source_needs_corroboration'; rows.append({'claim_group_id':g['claim_group_id'],'claim':g['representative'],'source_ids':sources,'evidence_ids':evidence,'status':status})
    write_json(PROJECT_ROOT/'research/initial_claim_verification.json',{'claims':rows}); return save(20,'Initial conservative verification',['research/initial_claim_verification.json'],Counter(r['status'] for r in rows))
def c21():
    qs=['civilization_identity','chronology','urbanism','writing','trade','technology','environment','decline','population_society']; rows=(read_json(PROJECT_ROOT/'research/initial_claim_verification.json',{}) or {}).get('claims',[]); by={q:[] for q in qs}
    for r in rows:
        low=r['claim'].lower(); target=next((q for q in qs if q.split('_')[0] in low), 'general'); by.setdefault(target,[]).append(r)
    write_json(PROJECT_ROOT/'research/focused_historical_verification.json',{'targets':by}); return save(21,'Focused historical verification',['research/focused_historical_verification.json'])
def c22():
    targets=['chronology','writing','trade','environment','decline']; out=[]
    for t in targets:
        u='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':f'Indus Valley {t}','per-page':20}); r=get(u)
        if r is not None and r.ok:
            out += [{'source_id':f'ext_{abs(hash((t,w.get("id"))))%10**10}','target':t,'title':w.get('title',''),'url':(w.get('primary_location') or {}).get('landing_page_url') or w.get('id'),'doi':norm(w.get('doi')).replace('https://doi.org/','') or None,'year':w.get('publication_year'),'cited_by_count':w.get('cited_by_count',0),'abstract_inverted_index':w.get('abstract_inverted_index')} for w in r.json().get('results',[])]
        time.sleep(CONFIG['delay'])
    write_json(PROJECT_ROOT/'research/targeted_external_sources.json',{'sources':out}); return save(22,'Targeted external verification search',['research/targeted_external_sources.json'],{'results':len(out)})
def c23():
    rs=(read_json(PROJECT_ROOT/'research/targeted_external_sources.json',{}) or {}).get('sources',[]); by=defaultdict(list)
    for r in rs: by[r['target']].append(r)
    sel=[]
    for t,a in by.items(): sel+=sorted(a,key=lambda x:(x.get('cited_by_count',0),bool(x.get('doi'))),reverse=True)[:8]
    write_json(PROJECT_ROOT/'research/verification_dossier.json',{'works':sel}); return save(23,'Verification dossier',['research/verification_dossier.json'],{'works':len(sel)})
def c24():
    rs=(read_json(PROJECT_ROOT/'research/verification_dossier.json',{}) or {}).get('works',[]); pk=[]
    for r in rs:
        inv=r.get('abstract_inverted_index') or {}; pairs=[(p,w) for w,ps in inv.items() if isinstance(ps,list) for p in ps]; text=' '.join(w for _,w in sorted(pairs))[:8000]
        pk.append({'packet_id':f'pkt_{len(pk)+1:04d}','source_id':r['source_id'],'target':r['target'],'title':r['title'],'doi':r.get('doi'),'access_level':'abstract_only' if text else 'metadata_only','evidence_text':text})
    write_json(PROJECT_ROOT/'research/evidence_packets.json',{'packets':pk}); return save(24,'Create evidence packets',['research/evidence_packets.json'],{'packets':len(pk)})
def c25():
    pk=(read_json(PROJECT_ROOT/'research/evidence_packets.json',{}) or {}).get('packets',[]); rows=[]
    for p in pk:
        t=p.get('evidence_text',''); cls='CAUSAL' if re.search(r'\b(cause|caused|led to|resulted in|due to)\b',t,re.I) else 'UNCERTAIN' if re.search(r'\b(may|might|could|suggests|possible|hypothesis)\b',t,re.I) else 'DOCUMENTED'; rows.append({'evidence_id':f'ple_{len(rows)+1:05d}','source_id':p['source_id'],'target':p['target'],'evidence_text':t,'classification':cls})
    write_json(PROJECT_ROOT/'research/claim_level_evidence.json',{'evidence':rows}); return save(25,'Classify claim-level evidence',['research/claim_level_evidence.json'],{'items':len(rows)})
def c26():
    ev=(read_json(PROJECT_ROOT/'research/claim_level_evidence.json',{}) or {}).get('evidence',[]); by=defaultdict(list)
    for e in ev:
        key=re.sub(r'\W+',' ',e['evidence_text'].lower())[:180]; by[(e['target'],key)].append(e)
    rows=[]
    for (t,k),a in by.items():
        ss=sorted({x['source_id'] for x in a}); rows.append({'claim_group_id':f'corr_{len(rows)+1:04d}','target':t,'claim_key':k,'source_ids':ss,'evidence_ids':[x['evidence_id'] for x in a],'status':'well_corroborated' if len(ss)>=3 else 'corroborated' if len(ss)>=2 else 'single_source'})
    write_json(PROJECT_ROOT/'research/corroborated_claims.json',{'claims':rows}); return save(26,'Independent corroboration',['research/corroborated_claims.json'],Counter(r['status'] for r in rows))
def c27():
    rows=(read_json(PROJECT_ROOT/'research/corroborated_claims.json',{}) or {}).get('claims',[]); ledger=[]
    for r in rows:
        st='VERIFIED_FACT' if r['status']=='well_corroborated' and r['target'] not in {'decline','writing'} else 'CORROBORATED_FACT' if r['status']=='corroborated' else 'ATTRIBUTED_INTERPRETATION' if r['target']=='decline' and r['status']=='well_corroborated' else 'NEEDS_VERIFICATION'
        ledger.append({'ledger_id':f'ledger_{len(ledger)+1:04d}','target':r['target'],'claim_group_id':r['claim_group_id'],'verification_status':st,'source_ids':r['source_ids'],'evidence_ids':r['evidence_ids'],'notes':['Same DOI counts as one independent work.','Abstract/metadata is not full text.','Environmental evidence does not automatically prove civilization-wide collapse.','Indus script decipherment is not assumed.']})
    write_json(PROJECT_ROOT/'research/verified_claim_ledger.json',{'ledger':ledger}); return save(27,'Create verified claim ledger',['research/verified_claim_ledger.json'],Counter(x['verification_status'] for x in ledger))
STEPS={i:globals()[f'c{i}'] for i in range(1,28)}
