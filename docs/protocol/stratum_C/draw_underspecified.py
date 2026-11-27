"""Stratum C underspecified slot, rule v2 (owner asked 2026-11-27 to complete the stratum; written before running).
Pool: the 'underspecified' search of search_terms.json (frozen frame AND short-format titles AND animal terms AND "pubmed pmc"[sb] NOT preprint[pt]),
minus PMIDs used in strata A/B or in other C slots, minus PMIDs judged ineligible in the first underspecified pass.
Feature scoring of the PMC Methods text: 7 extraction-critical items (species/strain, sex, age or weight, animals per group, dose/amount, route, duration/timepoints).
Eligible for the draw: Methods >= 1500 chars, animal species found, and >= 3 of the 7 items missing. Draw 12 with random.Random(20261114) from the eligible
pool sorted ascending; candidates are then read in draw order and the first 4 that are genuinely underspecified are taken."""
import csv,json,re,time,random,hashlib,urllib.request,urllib.parse,sys
from lxml import etree
SEED=20261114; TOOL='assist3r-pilot-validation'
P=r'c:\Users\leohm\AI_projects\Assist3R\docs\protocol'
FQ=json.load(open(P+r'\v3\manifest.json',encoding='utf-8'))['full_query']
T=json.load(open(P+r'\stratum_C\search_terms.json',encoding='utf-8'))
def call(ep,**kw):
    kw.update(db=kw.pop('db','pubmed'),tool=TOOL); data=urllib.parse.urlencode(kw).encode()
    for a in range(6):
        try: time.sleep(0.5); return urllib.request.urlopen(urllib.request.Request('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'+ep,data=data,headers={'User-Agent':TOOL+'/1.0'}),timeout=120).read()
        except Exception as e: err=e; time.sleep(3*(a+1))
    raise err
d=json.loads(call('esearch.fcgi',term=f'({FQ}) AND ({T["underspecified"]}) AND "pubmed pmc"[sb] NOT preprint[pt]',retmax=10000,retmode='json'),strict=False)['esearchresult']
ids=sorted(int(x) for x in d['idlist']); assert len(ids)==int(d['count'])
used=set()
for f in (P+r'\pubmed_extratum\stratum_B\stratum_B_screening.csv',P+r'\stratum_A\stratum_A_screening.csv'): used|={int(r['pmid']) for r in csv.DictReader(open(f,encoding='utf-8-sig'))}
C=list(csv.DictReader(open(P+r'\stratum_C\stratum_C_screening.csv',encoding='utf-8-sig')))
used|={int(r['pmid']) for r in C if r['slot']!='underspecified'}
used|={int(r['pmid']) for r in C if r['slot']=='underspecified' and r['screening_decision']=='exclude_proposed'}
pool=[i for i in ids if i not in used]; print('search',len(ids),'pool',len(pool),flush=True)
pmc={}
for i in range(0,len(pool),150):
    s=json.loads(call('esummary.fcgi',id=','.join(map(str,pool[i:i+150])),retmode='json'),strict=False)['result']
    for u in s['uids']:
        for a in s[u].get('articleids',[]):
            if a['idtype']=='pmc': pmc[int(u)]=a['value']
FL={'species':r'\b(C57BL|BALB|Sprague|Wistar|Lewis|CD-?1|ICR|Swiss|zebrafish|rats?|mice|mouse|pigs?|rabbits?|rodents?)\b','sex':r'\b(male|female|males|females)\b','age_weight':r'\b\d+(\.\d+)?\s*(weeks?|wk|months?|days?)[\s-]*old\b|\bweighing\b|\b\d+\s*(g|kg)\b|aged\s+\d','n_group':r'\bn\s*=\s*\d+|\b(\d+|ten|eight|six|five|four|three|two)\s+(animals|rats|mice|per group|rabbits|pigs)','dose':r'\b\d+(\.\d+)?\s*(mg|µg|μg|ug|ml|mL|mg/kg|%|mM|μM|µM)\b','route':r'\b(intraperitoneal|i\.p\.|intravenous|i\.v\.|oral|gavage|subcutaneous|s\.c\.|intranasal|intramuscular|topical|intravitreal|intratracheal|inhalation)\b','duration':r'\b\d+\s*(days?|weeks?|hours?|h|min|minutes)\b'}
feat={}
plist=[i for i in pool if i in pmc]
for k in range(0,len(plist),10):
    chunk=plist[k:k+10]
    raw=call('efetch.fcgi',db='pmc',id=','.join(pmc[i][3:] if pmc[i].startswith('PMC') else pmc[i] for i in chunk),retmode='xml')
    root=etree.fromstring(raw)
    for art in root.iterfind('.//article'):
        pid=None
        for a in art.iterfind('.//article-id'):
            if a.get('pub-id-type')=='pmid': pid=int(a.text)
        if pid is None: continue
        out=[]
        for s in art.iterfind('.//body/sec'):
            t=s.find('title'); h=''.join(t.itertext()).lower() if t is not None else ''
            if re.search(r'method|material|experimental|animal|procedure',h): out.append(re.sub(r'\s+',' ',' '.join(s.itertext())))
        m=' '.join(out); miss=[n for n,p in FL.items() if not re.search(p,m,re.I)]
        feat[pid]=dict(mlen=len(m),has_species='species' not in miss,missing=[x for x in miss if x!='species'] if 'species' not in miss else miss)
    if (k//10)%10==0: print('fetched',k,'of',len(plist),flush=True)
elig=sorted(i for i,f in feat.items() if f['mlen']>=1500 and f['has_species'] and len(f['missing'])>=3)
print('with features',len(feat),'| eligible (>=3 of 6 non-species items missing):',len(elig),flush=True)
rng=random.Random(SEED); pick=rng.sample(elig,min(12,len(elig)))
json.dump(dict(seed=SEED,search_hits=len(ids),pool=len(pool),with_pmc_features=len(feat),eligible=len(elig),draw=[dict(rank=r+1,pmid=p,missing=feat[p]['missing'],methods_chars=feat[p]['mlen'],pmcid=pmc[p]) for r,p in enumerate(pick)],script_sha256=hashlib.sha256(open(P+r'\stratum_C\draw_underspecified.py','rb').read()).hexdigest()),open(P+r'\stratum_C\underspecified_draw_v2.json','w',encoding='utf-8'),indent=1)
for r,p in enumerate(pick,1): print(r,p,pmc[p],feat[p]['mlen'],feat[p]['missing'],flush=True)
print('DONE',flush=True)
