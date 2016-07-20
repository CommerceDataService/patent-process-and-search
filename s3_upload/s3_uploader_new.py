import boto3, os, sys, logging, time


class S3Uploader(object):
    def __init__(self, bucket):
        self.sts_client = boto3.client('sts')
        self.s3 = boto3.resource('s3',
#                                 aws_access_key_id=self.credentials['AccessKeyId'],
#                                 aws_secret_access_key=self.credentials['SecretAccessKey'],
#                                 aws_session_token=self.credentials['SessionToken'],
                                 )

        self.bucket = self.s3.Bucket(bucket)

    def post_file(self, filename, fname, series):
        for x in range(1,10):
            try:
                with open(filename, 'rb') as data:
                    self.bucket.put_object(Key=series + '/' + fname, Body=data)

                return True

            except ConnectionError as e:

                logging.info("Caught connection error " + str(e) )
                time.sleep(x)

        logging.error("Exceeding maximum number of tries, giving up")
        sys.exit(2)

    def get_file_list(self, prefix):
        return self.bucket.objects.filter(Prefix=prefix)
