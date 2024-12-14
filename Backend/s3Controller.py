import boto3
from botocore.exceptions import ClientError
from Backend.errorEnums import S3UploadError, S3BucketError


class S3Controller:
    DEFAULT_REGION = 'eu-central-1'
    BUCKET_PREFIX = 'IaaS-6'

    def __init__(self):
        self.s3_client = self.get_s3_client()

    def get_s3_client(self):
        """Create a S3 cliente
        :return: S3 cliente in eu-central-1 region
        """
        return boto3.client('s3', region_name=self.DEFAULT_REGION)

    def create_empty_bucket(self, username):
        """Create an S3 bucket in eu-central-1 region

        :param username: Bucket name to create
        :return: True if bucket created, else False
        """

        if not self.__create_root_bucket():
            return S3BucketError.ROOT_BUCKET_NOT_CREATED
        try:
            bucket_name = f"{self.BUCKET_PREFIX}".lower()
            self.s3_client.put_object(Bucket=bucket_name, Key=f"{username}/")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(e)
            return error_code == 'BucketAlreadyOwnedByYou'

    def __create_root_bucket(self):
        """ Create root bucket in eu-central-1 region
        :return: True if bucket created, else False
        """
        location = {'LocationConstraint': self.DEFAULT_REGION}
        bucket_name = f"{self.BUCKET_PREFIX}".lower()

        try:
            self.s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(e)
            return error_code == 'BucketAlreadyOwnedByYou'

    def upload_file(self, file_to_upload, username, object_name):
        """Upload a file to user's S3 bucket

        :param file_to_upload: File to upload
        :param username: User's name to upload file
        :param object_name: S3 object name. We use date as name
        :return: True if file was uploaded, else False
        """

        try:
            bucket_name = f"{self.BUCKET_PREFIX}".lower()
            self.s3_client.put_object(Bucket=bucket_name, Key=f"{username}/{object_name}.bin", Body=file_to_upload)
            return True
        except ClientError as e:
            print(e)
            return False