from Backend.database import DatabaseAPI
from Backend.encrypter import Encrypter
from enum import Enum

class UserCreationError(Enum):
    NONE = "No errors"
    USERNAME_ALREADY_EXISTS = "The username already exists."
    INVALID_USERNAME = "The username is invalid."

class UserLoginError(Enum):
    NONE = "No errors"
    INVALID_USERNAME = "The username is invalid."
    INVALID_PASSWORD = "The password is invalid."
    USERNAME_DOES_NOT_EXIST = "The username does not exist."

class UsersController:
    """
    Class: User with full name, username, password, and an AWS KMS data key pair.
    """

    def __init__(self):
        self.database = DatabaseAPI()
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
        password_encrypted = Encrypter.encrypt_password(password, public_key)

        # TODO: check if username exits
        if DatabaseAPI.is_user_registered(username):
            return UserCreationError.USERNAME_ALREADY_EXISTS

        # TODO: save to data base
        #saveToDatabase(username, full_name, password_encrypted, public_key, cyphered_private_key)
        DatabaseAPI.register_user(username, full_name, password_encrypted, public_key, cyphered_private_key)

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
        encrypted_private_key = DatabaseAPI.get_user_private_key(username)

        # Decrypt user's password
        decrypted_password = Encrypter.decrypt_password(encrypted_password, encrypted_private_key)

        # TODO: compare password
        if password == decrypted_password:
            self.is_logged_in = True
            return UserLoginError.NONE
        else:
            return UserLoginError.INVALID_PASSWORD

    def get_user_messages(self):
        """
        If user is login, return messages from S3 bucket

        :return: a list of messages
        """
        # TODO: get all messages from S3 bucket

        # TODO: decrypt all messages with private key
        # TODO: get private key from database
        # encrypted_private_key = get_user_private_key(username)
        # Decrypt user's password
        # decrypted_password = Encrypter.decrypt_password(encrypted_password, encrypted_private_key)

        if self.is_logged_in:
            pass

        pass

