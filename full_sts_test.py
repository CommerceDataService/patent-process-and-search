import time

import sys

from s3_upload.s3_uploader import S3Uploader

count = 0


class TestRun(object):
    def __init__(self):
        self.uploader = S3Uploader('uspto-bdr')

    def single_run(self):
        print("   Doing bucket list")
        files = self.uploader.get_file_list("13/130000")
        files = list(files)

        print("   Retrieved %d object names" % len(files))
        print("   First Obj %s " % files[0].key)

        file = files[0].get()

        body = file['Body'].read()

        print("   Object starts with %s " % body[0:20])

    def do_test(self):
        end = 900
        for i in range(1, end):
            print("Run %d/%d " % (i, end))

            self.single_run()

            print ("Sleep")
            sys.stdout.flush()
            time.sleep(20)


if __name__ == '__main__':
    print("Doing long term STS/S3 test")

    run = TestRun()
    run.do_test()
