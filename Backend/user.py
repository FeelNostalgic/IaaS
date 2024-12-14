from Crypto.SelfTest.Protocol.test_ecdh import private_key

from encrypter import Encrypter

class User:
    """
    Class: User with full name, username, password, and an AWS KMS data key pair.
    """

    def __init__(self):
        self.is_logged_in = False

    def register_user(self, full_name, username, password):
        """
        Save the user data to the database
        Generate key pair for the user

        :param full_name: Full name of the user.
        :param username: The unique username of the user.
        :param password: The password for the user account.
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
        # TODO: save to data base
        #saveToDatabase(username, full_name, password_encrypted, public_key, cyphered_private_key)


    def login_user(self, username, password):
        """
        Get password from database, decrypt it, and check if is correct
        Then log in the user

        :param username: The unique username of the user.
        :param password: The password for the user account.
        :return: Error message if
            - username does not exist
            - password is wrong
        """
        # TODO: check if username exits

        # TODO: get password from database
        #encrypted_password = get_user_password(username)

        # TODO: get private key from database
        #encrypted_private_key = get_user_private_key(username)

        # Decrypt user's password
        #decrypted_password = Encrypter.decrypt_password(encrypted_password, encrypted_private_key)

        # TODO: compare password
        #if(password == decrypted_password):
            #correct password
        #else:
            #incorrecto password

        self.is_logged_in = True

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

