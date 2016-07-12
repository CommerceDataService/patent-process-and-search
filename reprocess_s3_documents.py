import logging

import boto3

from s3_upload.s3_uploader import S3Uploader
from s3_upload.partitioner import Partitioner
from s3_upload.util import Util


def get_file_list(list_file):

    with open(list_file, "r") as runlist:
        for l in runlist:
            l = l.lstrip().rstrip()
            yield l

if __name__ == '__main__':
    print("Reprocess S3 documents")

    #logging configuration
    logging.basicConfig(
                        filename='reprocess-s3.log',
                        level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s -%(message)s',
                        datefmt='%Y%m%d %H:%M:%S'
                       )
    stderrLogger=logging.StreamHandler()
    stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    logging.getLogger().addHandler(stderrLogger)

    boto3.set_stream_logger('boto3.resources', logging.WARN)


    list_file = "run-list/run-list.txt"

    files = get_file_list(list_file)

    p = Partitioner(files)

    store = S3Uploader('uspto-bdr')

    n = 0

    for x in p.get_my_stream():

        obj = store.get_obj(x)
        meta = {}

        objdata = obj.get()

        n += 1
        logging.info('Processing #{}  [{}]'.format(n, x))

        jsontext = objdata['Body'].read()
        jsontext = Util.reprocess_document(jsontext, obj.key, meta)

        url = Util.get_store_url(meta)

        store.post_document(jsontext, url)

        logging.info('Done. Written to {}'.format(url))

    logging.info('{} documents processed'.format(n))





