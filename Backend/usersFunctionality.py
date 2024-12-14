class UsersFunctionality:
    """
    Different actions from users
    """

    def __init__(self):
        pass

    def get_all_users(self):
        """
        Return all registered users
        :return: A list of users
        """
        
        pass

    def send_message_to_registered_user(self, register_user, message):
        """
        Send message to a registered user.
        Add a date to the message, encrypt the message with public key and add it to the S3 bucket

        :param register_user: The unique username of the user.
        :param message: Text to be sent
        :return: Message to confirm that the message was sent
        """

        pass

