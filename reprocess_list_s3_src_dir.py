import os

from s3_upload.s3_uploader import S3Uploader

if __name__ == '__main__':
    print("Preparing list of S3 SRC dir")

    src_loc = os.environ['S3_SRC_PATH']
    print("Feeding from {}".format(src_loc))

    store = S3Uploader('uspto-bdr')
    list = store.get_file_list(src_loc)


    with open("src-list.txt",'w') as outfile:
        for x in list:
            outfile.write(x.key+'\n')
