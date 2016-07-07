import pytest


@pytest.fixture
def uploader():
    from s3_uploader import S3Uploader
    return S3Uploader('uspto-bdr')


def test_that_we_can_post_file_to_s3(uploader):
    uploader.post_file("test_file.txt")


def test_that_we_can_retrieve_list_of_files_s14(uploader):
    files = uploader.get_file_list("14")

    count = sum(1 for x in files)

    assert count == 170867


def test_that_we_can_retrieve_list_of_files_s13(uploader):

    files = uploader.get_file_list("13")

    count = sum(1 for x in files)
    assert count == 225708


def test_that_we_can_get_subset_of_data(uploader):

    files = uploader.get_file_list("13/130000")
    files = list(files)

    assert 152 == len(files)
    assert files[0].key == '13/13000002_HC0HIXUBPXXIFW4_Non-Final_Rejection.json'

    file = files[0].get()

    assert file['Body'].read().startswith(b'{"type": "oa", "appid": "13000002", '
                                          b'"ifwnumber": "HC0HIXUBPXXIFW4", "documentcode": "CTNF",')
