import boto3
import os


class S3Uploader(object):
    def __init__(self, bucket):
        self.role = os.environ['AWS_ROLE_ARN']
        self.sts_client = boto3.client('sts')

        assumedRoleObject = self.sts_client.assume_role(
            RoleArn=self.role,
            RoleSessionName="AssumeRoleSession1"
        )

        self.credentials = assumedRoleObject['Credentials']

        self.s3 = boto3.resource('s3',
                                 aws_access_key_id=self.credentials['AccessKeyId'],
                                 aws_secret_access_key=self.credentials['SecretAccessKey'],
                                 aws_session_token=self.credentials['SessionToken'],
                                 )

        self.bucket = self.s3.Bucket(bucket)

    def post_file(self, filename):
        data = open(filename, 'rb')
        self.bucket.put_object(Key='TestObject', Body=data)
