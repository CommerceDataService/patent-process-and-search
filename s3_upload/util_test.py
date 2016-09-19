import os

import pytest


@pytest.fixture
def util():
    from util import Util
    return Util()

@pytest.fixture
def json_doc():
    return load_file("test_fixtures/test13_99_1.json")


@pytest.fixture
def json_doc_2():
    return load_file("test_fixtures/test13_99_2.json")


@pytest.fixture
def json_doc_3():
    return load_file("test_fixtures/test14_397_1.json")

@pytest.fixture
def json_doc_4():
    return load_file("test_fixtures/test14_999_1.json")

@pytest.fixture
def json_doc_5_wes():
    return load_file("test_fixtures/test14w_33_1.json")

@pytest.fixture
def json_doc_6_froms3():
    return load_file("test_fixtures/test13s3_06.json")

@pytest.fixture
def json_doc_7_s3_no_abdt():
    return load_file("test_fixtures/test13s3_038.json")


@pytest.fixture
def json_doc_8_s3_no_docdt():
    return load_file("test_fixtures/test14s3_001_bad_docdt.json")


def load_file(name):
    fd = open(name, "rb")
    data = fd.read()
    return data


def test_that_we_get_dirname_from_filename_wes(util):
    dir = util.log_directory("14s/14000008_I88ZIA17PXXIFW4_Non-Final_Rejection.json")
    assert dir == '14s/1400/000/8'

def test_that_we_get_dirname_from_filename_wes2(util):
    dir = util.log_directory("14s/14123458_I88ZIA17PXXIFW4_Non-Final_Rejection.json")
    assert dir == '14s/1412/345/8'


def test_that_we_get_dirname_from_filename(util):
    dir = util.log_directory("13/13000099_HM26I7FZPXXIFW4_Non-Final_Rejection.json")
    assert dir == '13/1300/009/9'


def test_that_we_not_dropping_anything_when_getting_dirname(util):
    dir = util.log_directory("13/13123478_HM26I7FZPXXIFW4_Non-Final_Rejection.json")
    assert dir == '13/1312/347/8'


def test_that_we_get_correct_doc_id(util):
    dir = util.doc_id("13/13123478_HM26I7FZPXXIFW4_Non-Final_Rejection.json")
    assert dir == '13123478, HM26I7FZPXXIFW4'


def test_we_get_correct_secondary_log_dir(util):

    sec_dir = util.secondary_log_directory("13/13123478_HM26I7FZPXXIFW4_Non-Final_Rejection.json")
    assert sec_dir == '13s/1312/347/8'


def test_we_can_convert_date_to_text(util):

    rv = util.convertUTCtoText("1471553120")
    assert rv == "08/18/2016"



def test_can_parse_json_file(util, json_doc):

    assert type(json_doc) == bytes
    assert len(json_doc) == 40292

    obj = util.parse_json(json_doc)

    assert obj['type'] == 'oa'
    assert obj['appid'] == '13000099'
    assert "\n" in obj['textdata']


def test_can_reprocess_document(util, json_doc):

    jsontext = util.reprocess_document(json_doc, '13/0000_XXX')

    assert type(jsontext) == str
    assert 's3_url' in jsontext
    assert '"s3_url": "13/0000_XXX' in jsontext

def test_we_can_retrieve_metadata_from_reprocessed_doc(util, json_doc):

    meta = {}

    util.reprocess_document(json_doc, '13/0000_XXX', meta)

    assert type(meta) == dict
    assert meta['appid'] == '13000099'
    assert meta['ifwnumber'] == 'I0XTDP9BPXXIFW4'
    assert meta['type'] == 'OA'
    assert meta['documentcode'] == 'CTFR'
    assert meta['series'] == '13'
    assert meta['format'] == 'json'


def test_we_can_get_store_url_from_metadata(util, json_doc):

    meta = {}
    util.reprocess_document(json_doc, '13/0000_XXX', meta)

    url = util.get_store_url(meta)

    assert url == 'OA/13/13000099_I0XTDP9BPXXIFW4_CTFR.json'



def test_that_we_reprocess_s3_file(util, json_doc_6_froms3):

    os.environ["PIPELINE_URL"] = 'http://scheduler.bdr.uspto.gov/go/tab/build/detail/Test/12/CMS_Pull/1/ComputeDelta'

    fd = open("before.doc.json", "wb")
    fd.write(json_doc_6_froms3)

    jsontext = util.reprocess_document(json_doc_6_froms3, '13/0000_XXX')

    fd = open("reprocessed_doc.json", "wb")
    fd.write(jsontext.encode("utf-8"))


    assert type(jsontext) == str
    assert 'doc_date' not in jsontext
    assert 'textdata' not in jsontext
    assert 'textdata_short' not in jsontext
    assert '"s3_url": "13/0000_XXX' in jsontext
    assert '"body_tx": "' in jsontext
    assert "patent_issue_dt_tx" in jsontext
    assert "patent_issue_dt_tx" in jsontext
    assert "patent_issue_dt_txt" not in jsontext
    assert '"patent_issue_dt_tx": "04/07/2015"' in jsontext
    assert '"doc_dt": "1387256400"' in jsontext
    assert '"doc_dt_tx": "12/17/2013"' in jsontext
    assert '"uniq_id": "13000006-HP5IYPUSPXXIFW4"' in jsontext
    assert '"body_short_tx": "DETAILED ACTION' in jsontext
    assert '"prov": "wasDerivedFrom(13/0000_XXX,.,' \
           'http://scheduler.bdr.uspto.gov/go/tab/build/detail/Test/12/CMS_Pull/1/ComputeDelta)"' in jsontext

def test_reprocess_removes_NaN_from_dn_intppty_cust_no(util, json_doc_2):

    jsontext = util.reprocess_document(json_doc_2, '13/0000_XXX')

    assert type(jsontext) == str
    assert 'dn_intppty_cust_no' not in jsontext



def test_reprocess_removes_NaN_should_be_no_nan_in_wipo_pub_no (util, json_doc_2):

    jsontext = util.reprocess_document(json_doc_2, '13/0000_XXX')

    assert 'wipo_pub_no' not in jsontext



def test_reprocess_preserves_good_wipo_pub_no (util, json_doc_3):

    jsontext = util.reprocess_document(json_doc_3, '13/0000_XXX')

    assert '"wipo_pub_no": "122334"' in jsontext



def test_reprocess_removes_misspelled_fields(util, json_doc_3):

    jsontext = util.reprocess_document(json_doc_3, '13/0000_XXX')
    assert 'dn_dw_gau_cd' not in jsontext


def test_reprocess_keeps_all_core_fields(util, json_doc):

    jsontext = util.reprocess_document(json_doc, '13/0000_XXX')

    for fld in ('"appid":', '"ifwnumber":', '"body_tx":', '"doc_dt":', '"type":', '"documentcode":'):
        assert fld in jsontext


def test_reprocess_keeps_all_core_fields_wes(util, json_doc_5_wes):

    jsontext = util.reprocess_document(json_doc_5_wes, '13/0000_XXX')

    for fld in ('"appid":', '"ifwnumber":', '"body_tx":', '"doc_dt":',
                '"type":', '"documentcode":', '"staging_src_path"'):
        assert fld in jsontext


def test_reprocess_removes_misspelled_fields_wes(util, json_doc_5_wes):

    jsontext = util.reprocess_document(json_doc_5_wes, '13/0000_XXX')
    assert 'dn_dw_gau_cd' not in jsontext


def test_reprocess_we_handle_empty_abandon_dt(util, json_doc_7_s3_no_abdt):

    jsontext = util.reprocess_document(json_doc_7_s3_no_abdt, '13/0000_XXX')
    assert 'abandon_dt' not in jsontext

def test_reprocess_we_handle_empty_doc_dt(util, json_doc_8_s3_no_docdt):

    jsontext = util.reprocess_document(json_doc_8_s3_no_docdt, '13/0000_XXX')
    assert 'doc_date' not in jsontext
    assert 'doc_dt' not in jsontext
    assert 'doc_dt_tx' not in jsontext




def test_reprocess_file_dt_is_processed_correctly(util, json_doc_3):

    jsontext = util.reprocess_document(json_doc_3, '13/0000_XXX')

    assert '"file_dt": "1376884800"' in jsontext

def test_reprocess_file_dt_is_processed_correctly_wes(util, json_doc_5_wes):

    jsontext = util.reprocess_document(json_doc_5_wes, '13/0000_XXX')

    assert '"file_dt": "1376625600"' in jsontext

def test_reprocess_file_wipo_no_is_handled_right(util, json_doc_5_wes):

    jsontext = util.reprocess_document(json_doc_5_wes, '13/0000_XXX')

    assert 'wipo_pub_no' not in jsontext

def test_reprocess_file_dt_is_formatted_as_proper_decimal(util, json_doc_4):

    jsontext = util.reprocess_document(json_doc_4, '13/0000_XXX')

    assert '"file_dt": "1381291200"' in jsontext


def test_date_conversion_is_working(util):

    rv = util.convertToUTC('19-AUG-13', '%d-%b-%y')
    assert rv == 1376884800


def test_we_allow_patch_up_objects(util):

    assert util.allowed_key("13/132000")
    assert util.allowed_key("13/133222")
    assert util.allowed_key("13/13624454")
    assert util.allowed_key("13/13773434")


def test_we_do_not_allow_other_objects(util):

    assert not util.allowed_key("13/130000")
    assert not util.allowed_key("13s/133222")
    assert not util.allowed_key("14/14624454")
    assert not util.allowed_key("13/13073434")
    assert not util.allowed_key("13/13173434")
    assert not util.allowed_key("13/13973434")
    assert not util.allowed_key("13/13473434")
    assert not util.allowed_key("13/13573434")
    assert not util.allowed_key("13/13873434")
