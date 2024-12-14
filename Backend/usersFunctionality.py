from Backend.encrypter import Encrypter
from Backend.errorEnums import S3UploadError
from Backend.database import DatabaseAPI
from datetime import datetime
from Backend.s3Controller import S3Controller

class UsersFunctionality:
    """
    Different actions from users
    """

    def __init__(self):
        self.s3Controller = S3Controller()
        pass

    @staticmethod
    def get_all_users():
        """
        Return all registered users
        :return: A list of users
        """
        # TODO: get user from database
        return DatabaseAPI.get_all_users()

    def send_message_to_registered_user(self, register_username, message):
        """
        Send message to a registered user.
        Add a date to the message, encrypt the message with public key and add it to the S3 bucket

        :param register_username: The unique username of the user.
        :param message: Text to be sent
        :return: Message to confirm that the message was sent
        """
        # TODO: get register_user public key from database
        public_key = DatabaseAPI.get_user_public_key(register_username)

        # Encrypt message with public key
        encrypted_message = Encrypter.encrypt_data(message, public_key)

        # Get date and format as DD-MM-YY-hh-mm
        date = datetime.now()
        format_date = date.strftime("%d-%m-%y-%H-%M")

        # TODO: save message in S3 bucket
        file_uploaded = self.s3Controller.upload_file(encrypted_message, register_username, format_date)

        if file_uploaded:
            return S3UploadError.NONE
        else:
            return S3UploadError.S3_FILE_NOT_UPLOADED