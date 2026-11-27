"""Stratum C candidate draw (protocol section 3.4). One random.Random(SEED), fixed order:
 1) rng.sample 6 of 12 near-miss families (file order)  2) rng.sample 5 of 8 no-match areas (file order)
 3) per slot in that order: all PMIDs matching frame+terms+"pubmed pmc"[sb] NOT preprint[pt], sorted ascending, minus PMIDs already
    used in strata A/B or earlier C slots, then rng.sample(K). Underspecified uses one pool and K_UNDER candidates.
Candidates are screened in draw order."""
import csv,json,time,random,hashlib,datetime,urllib.request,urllib.parse
from lxml import etree
SEED=20261114; K=6; K_UNDER=12; TOOL='assist3r-pilot-validation'
P=r'c:\Users\leohm\AI_projects\Assist3R\docs\protocol'
FQ=json.load(open(P+r'\v3\manifest.json',encoding='utf-8'))['full_query']
T=json.load(open(P+r'\stratum_C\search_terms.json',encoding='utf-8'))
def call(ep,**kw):
    kw.update(db='pubmed',tool=TOOL); data=urllib.parse.urlencode(kw).encode()
    for a in range(5):
        try:
            time.sleep(0.4); return urllib.request.urlopen(urllib.request.Request('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'+ep,data=data,headers={'User-Agent':TOOL+'/1.0'}),timeout=90).read()
        except Exception as e: err=e; time.sleep(2*(a+1))
    raise err
def _esearch(term,retstart=0,retmax=10000):
    for a in range(6):
        try: return json.loads(call('esearch.fcgi',term=term,retmax=retmax,retstart=retstart,retmode='json'),strict=False)['esearchresult']
        except Exception as e: err=e; time.sleep(3*(a+1))
    raise err
def search_all(term,lo=1,hi=2147483647):
    """All PMIDs for term. ESearch cannot page past 10,000, so large pools are split into disjoint PMID ranges (term unchanged)."""
    q=term if (lo,hi)==(1,2147483647) else f'({term}) AND ({lo}:{hi}[uid])'
    d=_esearch(q,retmax=0); n=int(d['count'])
    if n<=9500:
        if n==0: return [],d
        d2=_esearch(q,retmax=10000); ids=sorted(int(x) for x in d2['idlist']); assert len(ids)==n,'truncated'; return ids,d
    mid=(lo+hi)//2; a,_=search_all(term,lo,mid); b,_=search_all(term,mid+1,hi); ids=sorted(a+b); assert len(ids)==n,'range split not additive'; return ids,d
used=set()
for f in (P+r'\pubmed_extratum\stratum_B\stratum_B_screening.csv',P+r'\stratum_A\stratum_A_screening.csv'):
    used|={int(r['pmid']) for r in csv.DictReader(open(f,encoding='utf-8-sig'))}
rng=random.Random(SEED)
fams=[k for k in T['near_miss'] if not k.startswith('_')]; areas=[k for k in T['no_match'] if not k.startswith('_')]
slots=[('near_miss',f,T['near_miss'][f],K) for f in rng.sample(fams,6)]+[('no_match',a,T['no_match'][a],K) for a in rng.sample(areas,5)]+[('underspecified','Short-format animal articles',T['underspecified'],K_UNDER)]
draws=[];man=[]
for typ,name,terms,k in slots:
    ids,d=search_all(f'({FQ}) AND ({terms}) AND "pubmed pmc"[sb] NOT preprint[pt]')
    pool=[i for i in ids if i not in used]
    pick=rng.sample(pool,min(k,len(pool))); used.update(pick)
    man.append(dict(type=typ,name=name,hits=len(ids),pool_after_dedup=len(pool),drawn=len(pick),terms_sha256=hashlib.sha256(terms.encode()).hexdigest()[:16]))
    for rank,p in enumerate(pick,1): draws.append(dict(slot=typ,difficulty_type_intended={'near_miss':'near miss','no_match':'no match expected','underspecified':'underspecified'}[typ],family_or_area=name,draw_rank=rank,pmid=p,rng_seed=SEED,search_date=datetime.date.today().isoformat(),discovery_source='pubmed_frame',search_terms=terms))
pm=[str(x['pmid']) for x in draws]; meta={}
for i in range(0,len(pm),50):
    chunk=pm[i:i+50]
    s=json.loads(call('esummary.fcgi',id=','.join(chunk),retmode='json'),strict=False)['result']
    x=etree.fromstring(call('efetch.fcgi',id=','.join(chunk),retmode='xml')); ab={}
    for art in x.iterfind('.//PubmedArticle'):
        ab[art.findtext('.//MedlineCitation/PMID')]=' '.join(''.join(t.itertext()) for t in art.iterfind('.//Abstract/AbstractText'))
    for u in s['uids']:
        e=s[u]; ids_={a['idtype']:a['value'] for a in e.get('articleids',[])}
        meta[u]=dict(title=e.get('title',''),journal=e.get('source',''),pubdate=e.get('pubdate',''),pubtype='; '.join(e.get('pubtype',[])),doi=ids_.get('doi',''),pmcid=ids_.get('pmc',''),abstract=ab.get(u,''),pubmed_url=f'https://pubmed.ncbi.nlm.nih.gov/{u}/')
rows=[{**d,**meta[str(d['pmid'])],'screening_decision':'pending','exclusion_reason':'','procedure_id':'','methods_accessible':'','source_group':'','reviewer_notes':''} for d in draws]
with open(P+r'\stratum_C\stratum_C_screening.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
json.dump(dict(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seed=SEED,k=K,k_underspecified=K_UNDER,frame_query_sha256=hashlib.sha256(FQ.encode()).hexdigest(),slots=man,script_sha256=hashlib.sha256(open(P+r'\stratum_C\draw_C.py','rb').read()).hexdigest(),status='unverified_candidate_draw'),open(P+r'\stratum_C\draw_manifest.json','w',encoding='utf-8'),indent=1)
for m in man: print(m)
print(len(rows),'candidate rows')
