"""Draw the 30 reference-extraction cases (protocol section 4), Basket 1 only. Written 2026-11-27 before running.

Adaptation: section 4 assumes four strata (7-8 each); with Stratum D dropped, 10 per stratum (A, B, C).
Rules, one random.Random(20261116), fixed order:
  1) Stratum C: all 4 underspecified cases (protocol: at least 4) + 3 of 6 near-miss + 3 of 5 no-match, sampled from lists sorted by PMID.
  2) Stratum A: 10 of 17, sampled from the list sorted by method_id.
  3) Stratum B: 10 of 20, sampled from the list sorted by draw_position.
  4) Second-expert review: 10 of the 30, sampled from the list sorted by (stratum, procedure_id).
Expert-facing files carry only a blinded case id; the key (stratum, difficulty type, second review) is a separate file for the study team.
"""
import csv, json, os, random, re, shutil, hashlib, datetime
from lxml import etree

P = r'c:\Users\leohm\AI_projects\Assist3R\docs\protocol'
OUT = P + r'\reference'
PKG = OUT + r'\expert_package'
SEED = 20261116
norm = lambda d: re.sub(r'[^a-z0-9]', '', d.lower())


def rd(path):
    return list(csv.DictReader(open(path, encoding='utf-8-sig')))


A1 = [r for r in rd(P + r'\stratum_A\stratum_A_screening.csv') if r['procedure_id']]
A2 = [r for r in rd(P + r'\stratum_A\stratum_A_replacement_screening.csv') if r['procedure_id']]
for r in A1 + A2:
    r['stratum'] = 'A'
A = sorted(A1 + A2, key=lambda r: int(r['method_id']))
B = [r for r in rd(P + r'\pubmed_extratum\stratum_B\stratum_B_screening.csv') if r['screening_decision'] == 'include_proposed']
for r in B:
    r['stratum'] = 'B'
B.sort(key=lambda r: int(r['draw_position']))
Call = [r for r in rd(P + r'\stratum_C\stratum_C_screening.csv') if r['procedure_id']]
for r in Call:
    r['stratum'] = 'C'
assert len(A) == 17 and len(B) == 20 and len(Call) == 15, (len(A), len(B), len(Call))

rng = random.Random(SEED)
under = sorted([r for r in Call if r['slot'] == 'underspecified'], key=lambda r: int(r['pmid']))
nm = sorted([r for r in Call if r['slot'] == 'near_miss'], key=lambda r: int(r['pmid']))
no = sorted([r for r in Call if r['slot'] == 'no_match'], key=lambda r: int(r['pmid']))
C = under + rng.sample(nm, 3) + rng.sample(no, 3)
Asel = rng.sample(A, 10)
Bsel = rng.sample(B, 10)
chosen = Asel + Bsel + C
chosen_sorted = sorted(chosen, key=lambda r: (r['stratum'], r['procedure_id']))
second = set(id(r) for r in rng.sample(chosen_sorted, 10))

# blinded case ids: shuffle with the same stream so ids carry no stratum information
order = list(chosen)
rng.shuffle(order)
ARTICLES = os.listdir(P + r'\articles')


def find_source(r):
    pm = r['pmid']
    for f in ARTICLES:
        if f.lower().endswith('.pdf') and (f.split()[0] == pm or norm(f[:-4]) == norm(r.get('doi', ''))):
            return os.path.join(P, 'articles', f)
    for d in (P + r'\stratum_A\fulltext', P + r'\stratum_C\fulltext'):
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.startswith(pm + '_') and f.endswith('.xml'):
                    return os.path.join(d, f)
    return None


def xml_to_text(path):
    root = etree.parse(path).getroot()
    lines = []
    t = root.find('.//article-title')
    lines.append(re.sub(r'\s+', ' ', ''.join(t.itertext())) if t is not None else '')
    ab = root.find('.//abstract')
    if ab is not None:
        lines += ['', 'ABSTRACT', re.sub(r'\s+', ' ', ' '.join(ab.itertext()))]
    body = root.find('.//body')
    if body is not None:
        for el in body.iter():
            if el.tag == 'title':
                lines += ['', re.sub(r'\s+', ' ', ''.join(el.itertext())).upper()]
            elif el.tag == 'p' and el.getparent().tag != 'td':
                lines.append(re.sub(r'\s+', ' ', ''.join(el.itertext())))
            elif el.tag == 'caption':
                lines.append('[CAPTION] ' + re.sub(r'\s+', ' ', ''.join(el.itertext())))
            elif el.tag == 'table':
                for tr in el.iter('tr'):
                    lines.append('[TABLE ROW] ' + ' | '.join(re.sub(r'\s+', ' ', ''.join(c.itertext())) for c in tr))
    return '\n'.join(l for l in lines if l is not None)


os.makedirs(PKG + r'\sources', exist_ok=True)
key = []
tmpl = []
FIELDS = ['study_type', 'procedure_text', 'species', 'strain_or_line', 'sex', 'age_or_weight', 'animal_counts_total', 'animal_counts_per_group', 'route', 'dose_and_frequency', 'duration_and_timepoints', 'test_system', 'application', 'endpoints', 'regulatory_or_guideline_reference', 'unknown_or_not_stated_items', 'ask_for_clarification_yes_no', 'clarification_questions']
for n, r in enumerate(order, 1):
    cid = 'RC%02d' % n
    src = find_source(r)
    ext = os.path.splitext(src)[1] if src else ''
    dest = None
    if src:
        if ext.lower() == '.pdf':
            dest = PKG + r'\sources\%s.pdf' % cid
            shutil.copyfile(src, dest)
        else:
            dest = PKG + r'\sources\%s.txt' % cid
            open(dest, 'w', encoding='utf-8').write(xml_to_text(src))
    key.append(dict(case_id=cid, stratum=r['stratum'], procedure_id=r['procedure_id'], pmid=r['pmid'], doi=r.get('doi', ''),
                    method_or_slot=r.get('method_id') or r.get('draw_position') or r.get('family_or_area', ''),
                    difficulty_type_intended=r.get('difficulty_type_intended', ''), second_expert_review='yes' if id(r) in second else 'no',
                    title=r['title'], source_original=src or 'MISSING', source_expert_copy=os.path.basename(dest) if dest else 'MISSING'))
    tmpl.append(dict(case_id=cid, source_file=os.path.basename(dest) if dest else 'MISSING', expert_id='', minutes_spent='', **{f: '' for f in FIELDS}, expert_notes=''))
key.sort(key=lambda k: k['case_id'])
with open(OUT + r'\reference_case_key.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(key[0]))
    w.writeheader()
    w.writerows(key)
with open(PKG + r'\extraction_template.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(tmpl[0]))
    w.writeheader()
    w.writerows(sorted(tmpl, key=lambda t: t['case_id']))
json.dump(dict(seed=SEED, generated=datetime.datetime.now(datetime.timezone.utc).isoformat(), per_stratum=dict(A=10, B=10, C=10), c_composition='4 underspecified + 3 near-miss + 3 no-match',
               second_review=10, script_sha256=hashlib.sha256(open(OUT + r'\draw_reference_cases.py', 'rb').read()).hexdigest()),
          open(OUT + r'\reference_case_manifest.json', 'w', encoding='utf-8'), indent=1)
from collections import Counter
print('cases', len(key), Counter(k['stratum'] for k in key), 'second review', sum(k['second_expert_review'] == 'yes' for k in key))
print('missing sources:', [k['case_id'] for k in key if k['source_expert_copy'] == 'MISSING'])
print(Counter((k['stratum'], k['difficulty_type_intended']) for k in key if k['stratum'] == 'C'))
