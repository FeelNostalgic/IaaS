import boto3
from botocore.exceptions import ClientError

from Backend.config import AWS_REGION, S3_BUCKET_NAME
from Backend.database import DatabaseAPI
from Backend.encrypter import Encrypter
from Backend.errorEnums import S3UploadError, S3BucketError


class S3Controller:
    DEFAULT_REGION = AWS_REGION
    BUCKET_NAME = S3_BUCKET_NAME

    def __init__(self):
        self.s3_client = self.get_s3_client()

    def get_s3_client(self):
        """Create a S3 client
        :return: S3 client in the configured region
        """
        return boto3.client('s3', region_name=self.DEFAULT_REGION)

    def create_empty_bucket(self, username):
        """Create the root S3 bucket in the configured region

        All users share this single bucket, each under their own prefix.

        :param username: Prefix to reserve for the user
        :return: True if the bucket exists and the prefix was created, else False
        """

        if not self.__create_root_bucket():
            return S3BucketError.ROOT_BUCKET_NOT_CREATED
        try:
            bucket_name = self.BUCKET_NAME
            self.s3_client.put_object(Bucket=bucket_name, Key=f"{username}/")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(e)
            return error_code == 'BucketAlreadyOwnedByYou'

    def __create_root_bucket(self):
        """ Create root bucket in the configured region
        :return: True if bucket created, else False
        """
        location = {'LocationConstraint': self.DEFAULT_REGION}
        bucket_name = self.BUCKET_NAME

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
            bucket_name = self.BUCKET_NAME
            self.s3_client.put_object(Bucket=bucket_name, Key=f"{username}/{object_name}.bin", Body=file_to_upload)
            return True
        except ClientError as e:
            print(e)
            return False

    def upload_large_file(self, message_to_upload, encrypted_aes_key, nonce, tag, username, object_name):
        """Upload a file to user's S3 bucket

        :param message_to_upload: message to upload
        :param encrypted_aes_key: encrypted aes key to upload
        :param nonce: nonce to upload
        :param tag: tag to upload
        :param username: User's name to upload file
        :param object_name: S3 object name. We use date as name
        :return: True if file was uploaded, else False
        """

        try:
            bucket_name = self.BUCKET_NAME

            self.s3_client.put_object(Bucket=bucket_name, Key=f"{username}/{object_name}/message.bin", Body=message_to_upload)
            self.s3_client.put_object(Bucket=bucket_name, Key=f"{username}/{object_name}/encrypted_aes_key.bin", Body=encrypted_aes_key)
            self.s3_client.put_object(Bucket=bucket_name, Key=f"{username}/{object_name}/nonce.bin", Body=nonce)
            self.s3_client.put_object(Bucket=bucket_name, Key=f"{username}/{object_name}/tag.bin", Body=tag)
            return True
        except ClientError as e:
            print(e)
            return False

    def download_files(self, username):
        """
        Download all files from user's S3 bucket

        :param username: user's name to download files
        :return: a list of files downloaded
        """

        try:
            bucket_name = self.BUCKET_NAME
            objets = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=username)

            result = []

            for object in objets['Contents']:
                date = object['Key']

                object_s3 = self.s3_client.get_object(Bucket=bucket_name, Key=date)
                message = object_s3['Body'].read()
                if message != b'':
                    result.append((date, message))

            return result
        except ClientError as e:
            print(e)
            return []

    def download_large_files(self, username):
        """
        Download all files from user's S3 bucket

        :param username: user's name to download files
        :return: a dictionary of files downloaded (date, encrypted_message, encrypted_aes_key, nonce, tag)
        """

        try:
            bucket_name = self.BUCKET_NAME

            # check if bucket is empty
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f"{username}/", MaxKeys=1)
            if 'NextContinuationToken' not in response:
                return []

            objets = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f"{username}/", Delimiter='/')
            folders = [prefix['Prefix'] for prefix in objets['CommonPrefixes']]
            result = []

            for folder in folders:
                date = folder.split('/')[-2]
                objects = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f"{folder}")
                files = [obj['Key'] for obj in objects['Contents']]

                encrypted_message, encrypted_aes_key, nonce, tag = None, None, None, None

                for file_key in files:
                    if 'message' in file_key:
                        encrypted_message = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)['Body'].read()
                    elif 'encrypted_aes_key' in file_key:
                        encrypted_aes_key = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)['Body'].read()
                    elif 'nonce' in file_key:
                        nonce = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)['Body'].read()
                    elif 'tag' in file_key:
                        tag = self.s3_client.get_object(Bucket=bucket_name, Key=file_key)['Body'].read()

                if encrypted_message != b'':
                    result.append({
                        "date": date,
                        "encrypted_aes_key": encrypted_aes_key,
                        "nonce": nonce,
                        "tag": tag,
                        "encrypted_message": encrypted_message}
                    )
            return result
        except ClientError as e:
            print(e)
            return []
