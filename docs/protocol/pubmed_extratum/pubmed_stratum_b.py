#!/usr/bin/env python3
"""Reproducible probability sample of PubMed PMIDs without enumerating a huge frame.

Uses adaptive disjoint PMID/UID partitions, within a fixed publication-date
search frame: draw proportional to ESearch counts, descend selected branches,
and draw a uniform ESearch offset in a leaf with <= 9000 hits.
Publication dates are NOT suitable for partitions: electronic and print
publication dates may overlap. Count additivity is checked at every split.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

API = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
TOOL = 'Assist3RStratumBSampler'
FIELDS = ['draw_position','pmid','title','journal','pubdate','doi','pmcid','abstract','pubmed_url','full_text_url','screening_decision','exclusion_reason','procedure_id','methods_accessible','source_group','reviewer_notes']

class NCBI:
    def __init__(self, email, delay=0.4, attempts=5):
        self.email=email; self.delay=delay; self.attempts=attempts; self.last=0.; self.requests=0; self.unmatched_phrases=set()
    def get(self, endpoint, **params):
        params.update({'db':'pubmed','tool':TOOL,'email':self.email})
        # Large SYRCLE filters exceed URI length limits: use POST for ESearch.
        encoded=urllib.parse.urlencode(params).encode('utf-8')
        use_post=(endpoint=='esearch.fcgi')
        url=API+endpoint if use_post else API+endpoint+'?'+encoded.decode('ascii')
        request=urllib.request.Request(
            url, data=encoded if use_post else None,
            headers={'User-Agent': f'{TOOL}/1.0 ({self.email})',
                     **({'Content-Type':'application/x-www-form-urlencoded'} if use_post else {})},
            method='POST' if use_post else 'GET')
        for attempt in range(self.attempts):
            elapsed=time.monotonic()-self.last
            if elapsed < self.delay: time.sleep(self.delay-elapsed)
            self.last=time.monotonic()
            try:
                with urllib.request.urlopen(request,timeout=35) as response:
                    raw=response.read()
                self.requests+=1
                return raw
            except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as err:
                if isinstance(err,urllib.error.HTTPError) and err.code not in (429,500,502,503,504): raise
                if attempt==self.attempts-1: raise RuntimeError(f'NCBI request failed ({endpoint}): {err}') from err
                time.sleep(min(30,2**attempt+1))
        raise RuntimeError('Unreachable')
    def esearch(self, term, retstart=0, retmax=0):
        data=json.loads(self.get('esearch.fcgi',term=term,retmode='json',retstart=retstart,retmax=retmax,sort='pub_date'))
        if 'error' in data: raise RuntimeError(data['error'])
        out=data['esearchresult']
        errors = out.get('errorlist') or {}
        if errors.get('fieldsnotfound'):
            raise RuntimeError(f'PubMed invalid search fields: {errors["fieldsnotfound"]}')
        # In the published SYRCLE filter, rare animal names are OR alternatives.
        # PubMed may flag absent phrases even when a valid count and query
        # translation are returned. Record them; do not discard the sampling frame.
        for phrase in errors.get('phrasesnotfound', []):
            if phrase not in self.unmatched_phrases:
                self.unmatched_phrases.add(phrase)
                print(f'WARNING: PubMed could not match filter phrase: {phrase}', file=sys.stderr)
        if 'count' not in out or 'querytranslation' not in out:
            raise RuntimeError(f'Unexpected PubMed ESearch response: {out!r}')
        return int(out['count']),out.get('idlist',[]),out.get('querytranslation','')
    def efetch(self, pmids):
        return self.get('efetch.fcgi',id=','.join(pmids),retmode='xml',rettype='abstract')

def date_term(base,start,end):
    return f'({base}) AND ("{start:%Y/%m/%d}"[Date - Publication] : "{end:%Y/%m/%d}"[Date - Publication])'

def text_of(element):
    return ' '.join(''.join(element.itertext()).split()) if element is not None else ''

def parse_records(xml):
    root=ET.fromstring(xml)
    results={}
    for article in root.findall('.//PubmedArticle'):
        citation=article.find('MedlineCitation'); pubmed=article.find('PubmedData')
        pmid=text_of(citation.find('PMID')) if citation is not None else ''
        if not pmid: continue
        title=text_of(citation.find('.//ArticleTitle'))
        journal=text_of(citation.find('.//Journal/Title'))
        pubdate=text_of(citation.find('.//JournalIssue/PubDate'))
        abstract=' '.join(text_of(x) for x in citation.findall('.//Abstract/AbstractText'))
        dois=[]; pmcids=[]
        for x in pubmed.findall('.//ArticleId') if pubmed is not None else []:
            if x.attrib.get('IdType')=='doi': dois.append(text_of(x))
            if x.attrib.get('IdType')=='pmc': pmcids.append(text_of(x))
        pmcid=pmcids[0] if pmcids else ''
        results[pmid]={'pmid':pmid,'title':title,'journal':journal,'pubdate':pubdate,'doi':dois[0] if dois else '',
                       'pmcid':pmcid,'abstract':abstract,'pubmed_url':f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/',
                       'full_text_url':f'https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/' if pmcid else ''}
    return results

class Sampler:
    """Uniform without-replacement sampler over PubMed hits, conditional on a stable index.

    Use nonoverlapping numerical PMID/UID ranges, NOT publication-date ranges.
    Full publication date limits are applied to every query separately.
    """
    def __init__(self,client,base,start,end,seed,leaf_max=9000,uid_max=2147483647):
        self.client=client
        self.base=base
        self.start=start
        self.end=end
        self.rng=random.Random(seed)
        self.seed=seed
        self.leaf_max=leaf_max
        self.uid_max=uid_max
        self.count_cache={}
        self.translation={}
        self.splits=[]
        self.date_restricted_base=date_term(base,start,end)

    def query(self,lo,hi):
        return f'({self.date_restricted_base}) AND ({lo}:{hi}[uid])'

    def count(self,lo,hi):
        key=(lo,hi)
        if key not in self.count_cache:
            n,_,trans=self.client.esearch(self.query(lo,hi))
            self.count_cache[key]=n
            self.translation[key]=trans
        return self.count_cache[key]

    def check_frame(self):
        n,_,trans=self.client.esearch(self.date_restricted_base)
        self.base_count=n
        self.base_translation=trans
        uid_n=self.count(1,self.uid_max)
        if uid_n!=n:
            raise RuntimeError(
                f'UID RANGE DOES NOT COVER QUERY: date-only count={n}, '
                f'UID 1..{self.uid_max} count={uid_n}; stop, do not sample.')
        return n

    def split(self,lo,hi,parent_count):
        if lo>=hi:
            raise RuntimeError(f'One PMID has {parent_count} hits. Unexpected non-unique UID range.')
        mid=(lo+hi)//2
        left_n=self.count(lo,mid)
        right_n=self.count(mid+1,hi)
        if left_n+right_n!=parent_count:
            raise RuntimeError(
                f'INCONSISTENT UID PARTITION: {lo}..{hi} count={parent_count}, '
                f'children={left_n}+{right_n}. Stop; do not claim uniformity.')
        self.splits.append({'uid_start':lo,'uid_end':hi,'count':parent_count,
                            'left_count':left_n,'right_count':right_n})
        return (lo,mid,left_n),(mid+1,hi,right_n)

    def sample_one(self):
        lo,hi=1,self.uid_max
        count=self.count(lo,hi)
        if not count:
            raise RuntimeError('Sampling frame empty.')
        while count>self.leaf_max:
            left,right=self.split(lo,hi,count)
            chosen=left if self.rng.randrange(count)<left[2] else right
            lo,hi,count=chosen
        offset=self.rng.randrange(count)
        reported,ids,_=self.client.esearch(self.query(lo,hi),retstart=offset,retmax=1)
        if reported!=count:
            raise RuntimeError(f'PubMed count changed during draw in UID {lo}..{hi}: expected {count}, got {reported}. Restart.')
        if len(ids)!=1:
            raise RuntimeError(f'Expected one PMID at offset {offset}, got {ids!r}')
        pmid=ids[0]
        if not pmid.isdigit() or not (lo<=int(pmid)<=hi):
            raise RuntimeError(f'PubMed returned PMID {pmid!r} outside requested UID range {lo}..{hi}')
        return {'pmid':pmid,'uid_partition_start':lo,'uid_partition_end':hi,
                'offset':offset,'partition_count':count}

    def sample_unique(self,n):
        total=self.check_frame()
        if n>total:
            raise ValueError('Requested sample exceeds population')
        seen=set()
        result=[]
        attempts=0
        while len(result)<n:
            attempts+=1
            if attempts>max(1000,n*100):
                raise RuntimeError('Too many duplicate draws. Inspect frame and sampling.')
            item=self.sample_one()
            if item['pmid'] in seen: continue
            seen.add(item['pmid'])
            item['draw_position']=len(result)+1
            result.append(item)
        return result

def write_csv(path,rows,fieldnames):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=fieldnames,extrasaction='ignore');writer.writeheader();writer.writerows(rows)

def main(argv=None):
    p=argparse.ArgumentParser(description='Random PubMed Stratum B sampler (no need to download millions of PMIDs).')
    p.add_argument('--query-file',type=Path,required=True,help='UTF-8 plain text file with the frozen BASE query, excluding publication-date filters')
    p.add_argument('--email',required=True,help='Contact email required by NCBI')
    p.add_argument('--out',type=Path,default=Path('stratum_B_sample'))
    p.add_argument('--n',type=int,default=40)
    p.add_argument('--seed',type=int,default=20261113)
    p.add_argument('--start',default='2020-01-01')
    p.add_argument('--end',default='2025-12-31')
    p.add_argument('--leaf-max',type=int,default=9000)
    p.add_argument('--uid-max',type=int,default=2147483647,help='Upper limit of disjoint PubMed UID range; full-count coverage is checked')
    args=p.parse_args(argv)
    if args.uid_max<1: p.error('uid-max must be positive')
    if args.n<1 or args.leaf_max>9000 or args.leaf_max<1: p.error('n must be positive and leaf-max must be 1..9000')
    start=dt.date.fromisoformat(args.start);end=dt.date.fromisoformat(args.end)
    if start>end: p.error('start must not be after end')
    base=' '.join(args.query_file.read_text(encoding='utf-8').split())
    if not base: p.error('query file empty')
    if '[dp]' in base.lower() or '[date - publication]' in base.lower():
        p.error('Remove publication-date filters from the base query: the sampler adds them automatically')
    args.out.mkdir(parents=True,exist_ok=True)
    client=NCBI(args.email)
    sampler=Sampler(client,base,start,end,args.seed,args.leaf_max,args.uid_max)
    print('Checking frozen query and counts...',flush=True)
    records=sampler.sample_unique(args.n)
    print(f'Sampled {len(records)} distinct PMIDs from {sampler.base_count:,} records; retrieving citations...',flush=True)
    metadata={}
    for i in range(0,len(records),100):
        metadata.update(parse_records(client.efetch([x['pmid'] for x in records[i:i+100]])))
    if len(metadata)!=len(records):
        raise RuntimeError('EFetch did not return metadata for every PMID; no final outputs written')
    rows=[]
    for r in records:
        m=metadata[r['pmid']]
        rows.append({'draw_position':r['draw_position'],**m,'screening_decision':'pending','exclusion_reason':'','procedure_id':'','methods_accessible':'','source_group':'','reviewer_notes':''})
    write_csv(args.out/'stratum_B_screening.csv',rows,FIELDS)
    write_csv(args.out/'stratum_B_draw_audit.csv',records,list(records[0]))
    manifest={'status':'unverified_candidate_draw','generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
              'query_base':base,'query_sha256':hashlib.sha256(base.encode('utf-8')).hexdigest(),
              'full_query':date_term(base,start,end),'date_start':start.isoformat(),'date_end':end.isoformat(),
              'publication_frame_count':sampler.base_count,'sample_n':args.n,'seed':args.seed,
              'leaf_max':args.leaf_max,'method':'count-weighted recursive disjoint PMID/UID range sampling + uniform leaf ESearch offset + duplicate rejection',
              'consistency_checked_splits':sampler.splits,'base_query_translation':sampler.base_translation,'uid_max':sampler.uid_max,'counts':[
                  {'uid_start':k[0],'uid_end':k[1],'n':v,'query_translation':sampler.translation[k]}
                  for k,v in sorted(sampler.count_cache.items())],
              'request_count':client.requests,'pubmed_unmatched_phrases':sorted(client.unmatched_phrases),
              'important_limits':[
                  'PubMed is mutable; this is reproducible against a stable index, not a permanently frozen corpus',
                  'Candidate PMIDs must be manually screened in draw order until 20 eligible cases',
                  'Any changed count or nonadditive UID partition aborts sampling',
                  'Base query needs pre-run expert review for animal-study sensitivity and original-study eligibility']}
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    print(f'Done: {args.out / "stratum_B_screening.csv"}; manually screen in draw_position order.',flush=True)

if __name__=='__main__':main()
