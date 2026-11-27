"""Stratum A step 2: ordered candidate draw per selected method (protocol §3.2 step 3).
One random.Random(SEED) shared across methods, in the row order of stratum_A_method_selection.csv.
Per method: list all PMIDs matching (frozen v3 frame) AND terms NOT preprint[pt], sorted ascending, drop PMIDs already
drawn for earlier methods, then rng.sample(K). Candidates are screened in draw order; the first eligible is the case."""
import csv,json,time,random,hashlib,sys,datetime,urllib.request,urllib.parse
from lxml import etree
SEED=20261113; K=5; TOOL='assist3r-pilot-validation'
P=r'c:\Users\leohm\AI_projects\Assist3R\docs\protocol'
FQ=json.load(open(P+r'\v3\manifest.json',encoding='utf-8'))['full_query']
T=json.load(open(P+r'\stratum_A\search_terms.json',encoding='utf-8'))
sel=list(csv.DictReader(open(P+r'\stratum_A\stratum_A_method_selection.csv',encoding='utf-8-sig')))
def call(ep,**kw):
    kw.update(db='pubmed',tool=TOOL)
    data=urllib.parse.urlencode(kw).encode()
    for a in range(5):
        try:
            time.sleep(0.4)
            return urllib.request.urlopen(urllib.request.Request('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'+ep,data=data,headers={'User-Agent':TOOL+'/1.0'}),timeout=90).read()
        except Exception as e: err=e; time.sleep(2*(a+1))
    raise err
rng=random.Random(SEED); used=set(); draws=[]; manifest=[]
for r in sel:
    term=f'({FQ}) AND ({T[r["method_id"]]}) NOT preprint[pt]'
    d=json.loads(call('esearch.fcgi',term=term,retmax=10000,retmode='json'))['esearchresult']
    ids=sorted(int(x) for x in d['idlist']); assert len(ids)==int(d['count']),'result list truncated'
    pool=[i for i in ids if i not in used]; pick=rng.sample(pool,K); used.update(pick)
    manifest.append(dict(method_id=r['method_id'],oecd_ref=r['oecd_ref'],hits=len(ids),pool_after_dedup=len(pool),terms_sha256=hashlib.sha256(T[r['method_id']].encode()).hexdigest()[:16],translation_sha256=hashlib.sha256(d.get('querytranslation','').encode()).hexdigest()[:16]))
    for rank,p in enumerate(pick,1): draws.append(dict(method_id=r['method_id'],family=r['family'],oecd_ref=r['oecd_ref'],method_name=r['name'],draw_rank=rank,pmid=p))
pm=[str(x['pmid']) for x in draws]; meta={}
for i in range(0,len(pm),50):
    chunk=pm[i:i+50]
    s=json.loads(call('esummary.fcgi',id=','.join(chunk),retmode='json'))['result']
    x=etree.fromstring(call('efetch.fcgi',id=','.join(chunk),retmode='xml'))
    ab={}
    for art in x.iterfind('.//PubmedArticle'):
        pid=art.findtext('.//MedlineCitation/PMID'); ab[pid]=' '.join(''.join(t.itertext()) for t in art.iterfind('.//Abstract/AbstractText'))
    for u in s['uids']:
        e=s[u]; ids={a['idtype']:a['value'] for a in e.get('articleids',[])}
        meta[u]=dict(title=e.get('title',''),journal=e.get('source',''),pubdate=e.get('pubdate',''),epubdate=e.get('epubdate',''),pubtype='; '.join(e.get('pubtype',[])),doi=ids.get('doi',''),pmcid=ids.get('pmc',''),abstract=ab.get(u,''))
rows=[]
for d_ in draws:
    m=meta[str(d_['pmid'])]
    rows.append({**d_,**m,'pubmed_url':f'https://pubmed.ncbi.nlm.nih.gov/{d_["pmid"]}/','screening_decision':'pending','exclusion_reason':'','procedure_id':'','methods_accessible':'','source_group':'','reviewer_notes':''})
with open(P+r'\stratum_A\stratum_A_screening.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
json.dump(dict(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seed=SEED,candidates_per_method=K,frame='v3 manifest full_query (2020-2025) + method terms NOT preprint[pt]',frame_query_sha256=hashlib.sha256(FQ.encode()).hexdigest(),catalog_sha256=sel[0]['catalog_sha256'],methods=manifest,script_sha256=hashlib.sha256(open(P+r'\stratum_A\draw_articles.py','rb').read()).hexdigest(),status='unverified_candidate_draw'),open(P+r'\stratum_A\draw_manifest.json','w',encoding='utf-8'),indent=1)
print(len(rows),'candidate rows;',len(set(pm)),'distinct PMIDs')
