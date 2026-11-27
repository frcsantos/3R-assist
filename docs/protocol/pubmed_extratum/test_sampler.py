import unittest
from unittest.mock import patch
from pubmed_stratum_b import NCBI, parse_records

class TestNCBIAndMetadata(unittest.TestCase):
    def test_esearch_uses_post_for_long_query(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self):
                return b'{"esearchresult":{"count":"12","idlist":[],"querytranslation":"ok"}}'
        with patch('urllib.request.urlopen',return_value=FakeResponse()) as call:
            n, ids, trans=NCBI('researcher@example.org',delay=0).esearch('rat[tiab] OR '*1000)
        req=call.call_args.args[0]
        self.assertEqual(req.get_method(),'POST')
        self.assertNotIn('term=', req.full_url)
        self.assertIn(b'term=',req.data)
        self.assertEqual(n,12)

    def test_unmatched_or_terms_are_logged_not_fatal(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self):
                return b'{"esearchresult":{"count":"12","idlist":[],"querytranslation":"test","errorlist":{"phrasesnotfound":["poutings","chaffinchs"]}}}'
        with patch('urllib.request.urlopen',return_value=FakeResponse()):
            client=NCBI('researcher@example.org',delay=0)
            n,ids,trans=client.esearch('poutings[tiab] OR rat[tiab]')
        self.assertEqual(n,12)
        self.assertEqual(client.unmatched_phrases,{'poutings','chaffinchs'})

    def test_invalid_fields_remain_fatal(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self):
                return b'{"esearchresult":{"count":"12","idlist":[],"querytranslation":"test","errorlist":{"fieldsnotfound":["bogus"]}}}'
        with patch('urllib.request.urlopen',return_value=FakeResponse()):
            with self.assertRaisesRegex(RuntimeError,'invalid search fields'):
                NCBI('researcher@example.org',delay=0).esearch('rat[bogus]')

    def test_parse_xml(self):
        xml=b'<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>123</PMID><Article><ArticleTitle>Title</ArticleTitle><Journal><Title>Journal</Title><JournalIssue><PubDate><Year>2020</Year></PubDate></JournalIssue></Journal><Abstract><AbstractText>Abstract text</AbstractText></Abstract></Article></MedlineCitation><PubmedData><ArticleIdList><ArticleId IdType="doi">10.123/example</ArticleId></ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>'
        x=parse_records(xml)
        self.assertEqual(x['123']['doi'],'10.123/example')
        self.assertEqual(x['123']['abstract'],'Abstract text')

if __name__=='__main__':unittest.main()
