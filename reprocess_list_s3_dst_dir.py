import os
from s3_upload.s3_uploader import S3Uploader

if __name__ == '__main__':
    dst_loc = os.environ['S3_DST_PATH']

    test_pfx = ''

    if 'Test-' in os.environ['GO_PIPELINE_NAME']:
        test_pfx = "test/"

    dst_loc = test_pfx + dst_loc

    print("Preparing list of S3 DST dir")
    print("Feeding from {}".format(dst_loc))


    store = S3Uploader('uspto-bdr')
    list = store.get_file_list(dst_loc)

    with open("dst-list.txt", 'w') as outfile:
        for x in list:
            outfile.write(x.key + '\n')
