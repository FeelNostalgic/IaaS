from enum import Enum

class UserLoginError(Enum):
    NONE = "No errors"
    INVALID_USERNAME = "The username is invalid."
    INVALID_PASSWORD = "The password is invalid."
    USERNAME_DOES_NOT_EXIST = "The username does not exist."

class UserCreationError(Enum):
    NONE = "No errors"
    USERNAME_ALREADY_EXISTS = "The username already exists."
    INVALID_USERNAME = "The username is invalid."
    S3_BUCKET_NOT_CREATED = "The S3 bucket was not created."

class S3BucketError(Enum):
    NONE = "No errors"
    ROOT_BUCKET_NOT_CREATED = "The root bucket was not created."

class S3UploadError(Enum):
    NONE = "No errors"
    S3_FILE_NOT_UPLOADED = "The file was not uploaded to S3 bucket"
