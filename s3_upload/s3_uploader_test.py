import pytest


@pytest.fixture
def uploader():
    from s3_uploader import S3Uploader
    return S3Uploader('uspto-bdr')



def test_that_we_can_post_file_to_s3(uploader):
    uploader.post_file("test_file.txt")
