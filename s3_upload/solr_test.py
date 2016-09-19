import pytest
from solr import Solr, SolrException


@pytest.fixture
def solr():
    from solr import Solr
    return Solr('http://52.90.109.169:8983', 'oadata_3_shard1_replica1')


def test_we_can_poke_solr(solr):
    rv = solr.send_request('select?wt=json', '{}')
    assert rv['response']['numFound'] == 0


def test_we_can_add_field(solr):
    with pytest.raises(SolrException):
        rv = solr.add_field('s3_url', type="string", multi_valued=False)
        assert rv == 0
