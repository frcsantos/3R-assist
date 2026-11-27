"""Stratum A step 1 (protocol §3.2): proportional-by-family draw of 20 of the 47 B1 methods.
Usage: python select_methods.py <Tabelas.xlsx> <out.csv>   (seed fixed below)"""
import sys,json,csv,random,hashlib
import openpyxl
SEED=20261113; N=20
FAMILIES={  # method id -> family; ids from the `methods` sheet
 'Eye irritation and damage':[6,7,8,9,39,40,47,49],
 'Skin sensitisation':[10,11,12,13,14,15],
 'Genotoxicity':[17,18,19,45,46],
 'Skin irritation and corrosion':[1,3,4,5],
 'Acute oral toxicity':[22,23,24,25],
 'Endocrine activity':[41,42,43,44],
 'Rabies diagnostics':[30,33,34,35],
 'Absorption and clearance':[21,54,55],
 'Pyrogen and endotoxin':[20,38,56],
 'Phototoxicity':[16,50],
 'Reproductive toxicity':[36,37],
 'Fish embryo':[51,53],
}
src,out=sys.argv[1],sys.argv[2]
rows=list(openpyxl.load_workbook(src,read_only=True,data_only=True)['methods'].iter_rows(values_only=True))
h=rows[0]; ix={k:n for n,k in enumerate(h)}
M={int(r[0]):r for r in rows[1:]}
assert sorted(i for v in FAMILIES.values() for i in v)==sorted(M), 'family table must cover all methods exactly once'
total=len(M); quota={f:len(v)*N/total for f,v in FAMILIES.items()}
alloc={f:int(q) for f,q in quota.items()}
rem=sorted(FAMILIES,key=lambda f:(-(quota[f]-alloc[f]),list(FAMILIES).index(f)))
for f in rem[:N-sum(alloc.values())]: alloc[f]+=1
assert sum(alloc.values())==N
rng=random.Random(SEED); sha=hashlib.sha256(open(src,'rb').read()).hexdigest()
def en(x):
    try: return json.loads(x).get('en-us',x)
    except Exception: return x
out_rows=[]
for f,ids in FAMILIES.items():
    for mid in sorted(rng.sample(sorted(ids),alloc[f])):
        r=M[mid]
        try: avoided='; '.join(en(json.dumps(a['name'])) if False else a['name'].get('en-us','') for a in json.loads(r[ix['animal_procedures_avoided']]))
        except Exception: avoided=''
        out_rows.append(dict(family=f,family_size=len(ids),family_allocation=alloc[f],method_id=mid,slug=r[ix['slug']],name=en(r[ix['name']]),oecd_ref=r[ix['oecd_ref']] or '',animal_use=r[ix['animal_use']] or '',animal_procedures_avoided=avoided,seed=SEED,catalog_sha256=sha))
with open(out,'w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(out_rows[0]));w.writeheader();w.writerows(out_rows)
print('catalog sha256',sha); print({f:a for f,a in alloc.items()})
for r in out_rows: print(r['family'],'|',r['method_id'],'|',r['oecd_ref'] or r['slug'][:30],'|',r['name'][:55],'| avoided:',r['animal_procedures_avoided'][:70])
