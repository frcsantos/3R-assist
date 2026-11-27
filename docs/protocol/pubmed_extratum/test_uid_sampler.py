import re
import unittest
from pubmed_stratum_b import Sampler, date_term
import datetime as dt

class FakePubMed:
    def __init__(self, ids):
        self.ids=sorted(ids)
        self.unmatched_phrases=set()
        self.requests=0
    def esearch(self,term,retstart=0,retmax=0):
        self.requests+=1
        m=re.search(r'\((\d+):(\d+)\[uid\]\)',term)
        ids=self.ids
        if m:
            lo,hi=map(int,m.groups())
            ids=[x for x in ids if lo<=x<=hi]
        # A date term is in every query, regardless of UID partition.
        assert '[Date - Publication]' in term
        return len(ids), [str(x) for x in ids[retstart:retstart+retmax]],term

class TestUIDSampler(unittest.TestCase):
    def setUp(self):
        self.a=dt.date(2020,1,1)
        self.b=dt.date(2025,12,31)
        self.ids=[4,5,18,33,40,51,64,75,94,100]
    def create(self,seed=12):
        return Sampler(FakePubMed(self.ids),'animals',self.a,self.b,seed,leaf_max=3,uid_max=128)
    def test_full_unique_draw(self):
        s=self.create()
        values=s.sample_unique(len(self.ids))
        self.assertEqual({int(x['pmid']) for x in values},set(self.ids))
        self.assertGreater(len(s.splits),0)
    def test_reproducible(self):
        self.assertEqual(self.create().sample_unique(5),self.create().sample_unique(5))
    def test_uniform_first_draw(self):
        draws={n:0 for n in self.ids}
        for seed in range(2000):
            pmid=int(self.create(seed).sample_one()['pmid'])
            draws[pmid]+=1
        self.assertTrue(all(135<=x<=260 for x in draws.values()),draws)
    def test_nonadditive_rejected(self):
        class Broken(FakePubMed):
            def esearch(self,term,retstart=0,retmax=0):
                n,ids,t=super().esearch(term,retstart,retmax)
                if '(1:64[uid])' in term: n+=1
                return n,ids,t
        s=Sampler(Broken(self.ids),'animals',self.a,self.b,1,leaf_max=3,uid_max=128)
        with self.assertRaisesRegex(RuntimeError,'INCONSISTENT UID'):
            s.sample_unique(2)
    def test_frame_coverage_rejected(self):
        s=Sampler(FakePubMed(self.ids),'animals',self.a,self.b,1,leaf_max=3,uid_max=50)
        with self.assertRaisesRegex(RuntimeError,'UID RANGE DOES NOT COVER'):
            s.sample_unique(2)
    def test_range_query_with_date(self):
        s=self.create()
        q=s.query(17,42)
        self.assertIn('(17:42[uid])',q)
        self.assertIn('2020/01/01',q)
        self.assertIn('2025/12/31',q)

if __name__=='__main__':unittest.main()
