import unittest

from Backend.database import DatabaseAPI
from Backend.usersController import UsersController
from Backend.errorEnums import UserCreationError, UserLoginError, S3UploadError
from Backend.usersFunctionality import UsersFunctionality


class UsersControllerTest(unittest.TestCase):

    def setUp(self):
        self.user_data = {"username": "JohnD", "full_name": "John Doe", "password": "p1"}
        self.users_controller = UsersController()
        self.users_Functionality = UsersFunctionality()

    def tearDown(self):
        DatabaseAPI.delete_user(self.user_data["username"])

    def test_register_user_NO_ERROR(self):
        # Register User
        response = self.users_controller.register_user(self.user_data["username"], self.user_data["password"], self.user_data["full_name"])
        self.assertEqual(response, UserCreationError.NONE)

    def test_register_user_USERNAME_ALREADY_EXISTS(self):
        # Register User
        self.users_controller.register_user(self.user_data["username"], self.user_data["password"], self.user_data["full_name"])
        # Register User
        response = self.users_controller.register_user(self.user_data["username"], self.user_data["password"], self.user_data["full_name"])
        self.assertEqual(response, UserCreationError.USERNAME_ALREADY_EXISTS)

    def test_login_user_NO_ERROR(self):
        # Register User
        self.users_controller.register_user(self.user_data["username"], self.user_data["password"], self.user_data["full_name"])
        # Login User
        response = self.users_controller.login_user(self.user_data["username"], self.user_data["password"])
        self.assertEqual(response, UserLoginError.NONE)

    def test_send_message_to_user_NO_ERROR(self):
        # Register User
        self.users_controller.register_user(self.user_data["username"], self.user_data["password"], self.user_data["full_name"])
        response = self.users_Functionality.send_message_to_registered_user(self.user_data["username"], "test message")
        self.assertEqual(response, S3UploadError.NONE)

if __name__ == '__main__':
    unittest.main()
