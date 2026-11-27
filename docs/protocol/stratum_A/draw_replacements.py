"""Stratum A replacement draw (written 2026-11-27 before running).
Method choice: random.Random(20261113).choice([11,13,14,15]) replaces m10 (skin sensitisation);
m30 -> m33 and m34 -> m35 (the only unselected rabies methods); m50 -> m16 (the only unselected phototoxicity method).
Candidates: random.Random(20261115); per replacement method in the order [m10-repl, m33, m35, m16]: all PMIDs matching
frozen frame AND terms AND "pubmed pmc"[sb] NOT preprint[pt], sorted ascending, minus PMIDs already used in strata A, B, C or
earlier replacement slots, then rng.sample(6). Candidates are screened in draw order."""
import csv, json, time, random, hashlib, datetime, urllib.request, urllib.parse
import openpyxl
from lxml import etree

TOOL = 'assist3r-pilot-validation'
K = 6
P = r'c:\Users\leohm\AI_projects\Assist3R\docs\protocol'
FQ = json.load(open(P + r'\v3\manifest.json', encoding='utf-8'))['full_query']
T = json.load(open(P + r'\stratum_A\replacement_search_terms.json', encoding='utf-8'))
sel = {r['method_id']: r for r in csv.DictReader(open(P + r'\stratum_A\stratum_A_method_selection.csv', encoding='utf-8-sig'))}


def call(ep, **kw):
    kw.update(db='pubmed', tool=TOOL)
    data = urllib.parse.urlencode(kw).encode()
    err = None
    for a in range(6):
        try:
            time.sleep(0.5)
            req = urllib.request.Request('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/' + ep, data=data, headers={'User-Agent': TOOL + '/1.0'})
            return urllib.request.urlopen(req, timeout=120).read()
        except Exception as e:
            err = e
            time.sleep(3 * (a + 1))
    raise err


def search_all(term):
    d = json.loads(call('esearch.fcgi', term=term, retmax=10000, retmode='json'), strict=False)['esearchresult']
    ids = sorted(int(x) for x in d['idlist'])
    assert len(ids) == int(d['count'])
    return ids


m10_repl = random.Random(20261113).choice([11, 13, 14, 15])
slots = [('10', str(m10_repl), 'Skin sensitisation'), ('30', '33', 'Rabies diagnostics'), ('34', '35', 'Rabies diagnostics'), ('50', '16', 'Phototoxicity')]
print('replacement for m10 ->', m10_repl, flush=True)

wb = openpyxl.load_workbook(P + r'\Tabelas.xlsx', read_only=True, data_only=True)
mrows = list(wb['methods'].iter_rows(values_only=True))
ix = {k: n for n, k in enumerate(mrows[0])}
M = {int(r[0]): r for r in mrows[1:]}


def en(x):
    try:
        return json.loads(x).get('en-us', x)
    except Exception:
        return x


used = set()
for f in (P + r'\pubmed_extratum\stratum_B\stratum_B_screening.csv', P + r'\stratum_A\stratum_A_screening.csv', P + r'\stratum_C\stratum_C_screening.csv'):
    used |= {int(r['pmid']) for r in csv.DictReader(open(f, encoding='utf-8-sig'))}

rng = random.Random(20261115)
draws = []
man = []
for failed, repl, fam in slots:
    ids = search_all('(%s) AND (%s) AND "pubmed pmc"[sb] NOT preprint[pt]' % (FQ, T[repl]))
    pool = [i for i in ids if i not in used]
    pick = rng.sample(pool, min(K, len(pool)))
    used.update(pick)
    r = M[int(repl)]
    try:
        avoided = '; '.join(a['name'].get('en-us', '') for a in json.loads(r[ix['animal_procedures_avoided']]))
    except Exception:
        avoided = ''
    man.append(dict(replaces_method=failed, replacement_method=repl, family=fam, hits=len(ids), pool_after_dedup=len(pool), drawn=len(pick), terms_sha256=hashlib.sha256(T[repl].encode()).hexdigest()[:16]))
    for rank, p in enumerate(pick, 1):
        draws.append(dict(method_id=repl, replaces_method_id=failed, family=fam, oecd_ref=r[ix['oecd_ref']] or '', method_name=en(r[ix['name']]), animal_procedures_avoided=avoided, draw_rank=rank, pmid=p))

pm = [str(x['pmid']) for x in draws]
s = json.loads(call('esummary.fcgi', id=','.join(pm), retmode='json'), strict=False)['result']
x = etree.fromstring(call('efetch.fcgi', id=','.join(pm), retmode='xml'))
ab = {}
for art in x.iterfind('.//PubmedArticle'):
    ab[art.findtext('.//MedlineCitation/PMID')] = ' '.join(''.join(t.itertext()) for t in art.iterfind('.//Abstract/AbstractText'))
out = []
for d in draws:
    e = s[str(d['pmid'])]
    ids_ = {a['idtype']: a['value'] for a in e.get('articleids', [])}
    out.append({**d, 'title': e.get('title', ''), 'journal': e.get('source', ''), 'pubdate': e.get('pubdate', ''), 'pubtype': '; '.join(e.get('pubtype', [])), 'doi': ids_.get('doi', ''), 'pmcid': ids_.get('pmc', ''), 'abstract': ab.get(str(d['pmid']), ''), 'pubmed_url': 'https://pubmed.ncbi.nlm.nih.gov/%s/' % d['pmid'], 'screening_decision': 'pending', 'exclusion_reason': '', 'procedure_id': '', 'methods_accessible': '', 'source_group': '', 'reviewer_notes': '', 'seed': 20261115, 'catalog_sha256': sel['1']['catalog_sha256']})
with open(P + r'\stratum_A\stratum_A_replacement_screening.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0]))
    w.writeheader()
    w.writerows(out)
json.dump(dict(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), method_seed=20261113, article_seed=20261115, k=K, slots=man, script_sha256=hashlib.sha256(open(P + r'\stratum_A\draw_replacements.py', 'rb').read()).hexdigest(), status='unverified_candidate_draw'), open(P + r'\stratum_A\replacement_draw_manifest.json', 'w', encoding='utf-8'), indent=1)
for m in man:
    print(m)
print(len(out), 'candidate rows')
