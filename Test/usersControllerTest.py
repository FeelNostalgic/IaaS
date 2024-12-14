import unittest

from Backend.database import DatabaseAPI
from Backend.usersController import UsersController, UserCreationError, UserLoginError


class UsersControllerTest(unittest.TestCase):

    def setUp(self):
        self.user_data = {"username": "JohnD", "full_name": "John Doe", "password": "p1"}
        self.users_controller = UsersController()

    def tearDown(self):
        DatabaseAPI.delete_user(self.user_data["username"])
        pass

    def test_register_user_NO_ERROR(self):
        response = self.users_controller.register_user(self.user_data["username"], self.user_data["password"], self.user_data["full_name"])
        self.assertEqual(response, UserCreationError.NONE)

    def test_register_user_USERNAME_ALREADY_EXISTS(self):
        response = self.users_controller.register_user(self.user_data["username"], self.user_data["password"], self.user_data["full_name"])
        response = self.users_controller.register_user(self.user_data["username"], self.user_data["password"], self.user_data["full_name"])
        self.assertEqual(response, UserCreationError.USERNAME_ALREADY_EXISTS)

    def test_login_user_NO_ERROR(self):
        self.users_controller.register_user(self.user_data["username"], self.user_data["password"], self.user_data["full_name"])
        response = self.users_controller.login_user(self.user_data["username"], self.user_data["password"])
        self.assertEqual(response, UserLoginError.NONE)

if __name__ == '__main__':
    unittest.main()
