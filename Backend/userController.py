from Backend.errorEnums import UserCreationError, UserLoginError
from Backend.database import DatabaseAPI
from Backend.encrypter import Encrypter
from Backend.s3Controller import S3Controller


class UserController:
    """
    Class: User with full name, username, password, and an AWS KMS data key pair.
    """

    def __init__(self):
        self.username = None
        self.s3Controller = S3Controller()
        self.is_logged_in = False

    def register_user(self, username, password, full_name):
        """
        Save the user data to the database
        Generate key pair for the user

        :param full_name: Full name of the user. TODO: check if full_name is not empty (prob in frontend?)
        :param username: The unique username of the user. TODO: check if username is not empty (prob in frontend?)
        :param password: The password for the user account. TODO: check if password is not empty (prob in frontend?)
        public_key & cyphered_private_key must be created for each user
        then, save in database for future uses

        :return: Error message if:
            - username exits
        """
        # Generate key pair
        public_key, cyphered_private_key = Encrypter.generate_key_pair()

        # Encrypt password
        # TODO: check password strength (prob. in frontend before this method is called)
        password_encrypted = Encrypter.encrypt_data(password, public_key)

        # TODO: check if username exits
        if DatabaseAPI.is_user_registered(username):
            return UserCreationError.USERNAME_ALREADY_EXISTS

        # TODO: save to data base
        #saveToDatabase(username, full_name, password_encrypted, public_key, cyphered_private_key)
        DatabaseAPI.register_user(username=username, full_name=full_name, password=password_encrypted,
                                  public_key=public_key, cyphered_private_key=cyphered_private_key)

        # Create S3 bucket
        if not self.s3Controller.create_empty_bucket(username):
            return UserCreationError.S3_BUCKET_NOT_CREATED

        return UserCreationError.NONE

    def login_user(self, username, password):
        """
        Get password from database, decrypt it, and check if is correct
        Then log in the user

        :param username: The unique username of the user. TODO: check if username is not empty (prob in frontend?)
        :param password: The password for the user account. TODO: check if password is not empty (prob in frontend?)
        :return: Error message if
            - username does not exist
            - password is wrong
        """
        # TODO: check if username exits
        if not DatabaseAPI.is_user_registered(username):
            return UserLoginError.INVALID_USERNAME

        # TODO: get password from database
        encrypted_password = DatabaseAPI.get_user_password(username)

        # TODO: get private key from database
        encrypted_private_key = DatabaseAPI.get_user_cyphered_private_key(username)

        # Decrypt user's password
        decrypted_password = Encrypter.decrypt_data(encrypted_password, encrypted_private_key)

        # Compare password
        if password == decrypted_password:
            self.is_logged_in = True
            self.username = username
            return UserLoginError.NONE
        else:
            return UserLoginError.INVALID_PASSWORD

    def logout_user(self):
        """
        Close user session
        """
        self.is_logged_in = False
        self.username = None

    def get_user_messages(self):
        """
        If user is login, return messages from S3 bucket

        :return: a list of messages
        """
        if self.is_logged_in:
            # TODO: get all messages from S3 bucket
            all_messages_encrypted = self.s3Controller.download_large_files(self.username)

            # TODO: get private key from database
            encrypted_private_key = DatabaseAPI.get_user_cyphered_private_key(self.username)

            # decrypt all messages with private key
            result = []
            for encrypted_data in all_messages_encrypted:
                decrypted_message = Encrypter.decrypt_large_data(encrypted_data, encrypted_private_key)
                result.append({"date":encrypted_data["date"],"message":decrypted_message})

            return result