import boto3
import os
import datetime


def ensure_fresh_credentials(func):
    def wrapped_func(*args, **kwargs):
        uploader = args[0]
        if uploader.time_to_refresh():
            uploader.refresh_credentials()
            uploader.refresh_s3()

        return func(*args, **kwargs)

    return wrapped_func


class S3Uploader(object):
    def __init__(self, bucket_name):

        if 'AWS_ROLE_ARN' in os.environ:
            self.role = os.environ['AWS_ROLE_ARN']
        else:
            self.role = None

        self.sts_client = boto3.client('sts')
        self.expiration = datetime.datetime(2009, 1, 1, 1, 11, 24, 15, datetime.timezone.utc)
        self.bucket_name = bucket_name
        self.refresh_count = 0
        self.bucket = None
        self.credentials = None
        self.s3 = None

        self.test_pfx = ''

        if 'GO_PIPELINE_NAME' in os.environ:
            if 'Test-' in os.environ['GO_PIPELINE_NAME']:
                self.test_pfx = "test/"


    def refresh_s3(self):

        if self.credentials is None:
            self.s3 = boto3.resource('s3')
        else:
            self.s3 = boto3.resource('s3',
                                     aws_access_key_id=self.credentials['AccessKeyId'],
                                     aws_secret_access_key=self.credentials['SecretAccessKey'],
                                     aws_session_token=self.credentials['SessionToken'],
                                     )

        self.bucket = self.s3.Bucket(self.bucket_name)

    def time_to_refresh(self):

        current_time = datetime.datetime.now(datetime.timezone.utc)
        renew_time = current_time + datetime.timedelta(minutes=10)

        return renew_time > self.expiration

    def refresh_credentials(self):

        if self.role is None:
            self.credentials = None
            self.expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2160)
        else:

            assumed_role_object = self.sts_client.assume_role(
                RoleArn=self.role,
                RoleSessionName="AssumeRoleSession1"
            )

            self.credentials = assumed_role_object['Credentials']
            self.expiration = self.credentials['Expiration']

        self.refresh_count += 1
        self.bucket = None

        print("Refreshed Credentials. New expire time ", self.expiration)

    @ensure_fresh_credentials
    def post_file(self, filename, fname, series):
        data = open(filename, 'rb')
        self.bucket.put_object(Key=series + '/' + fname, Body=data)

    @ensure_fresh_credentials
    def get_file_list(self, prefix):
        return self.bucket.objects.filter(Prefix=prefix)

    @ensure_fresh_credentials
    def get_obj(self, key):
        return self.bucket.Object(key)

    def post_document(self, text, url):

        self.bucket.put_object(Key=self.test_pfx + url, Body=text)
