from flask import Flask
from Backend.usersController import UsersController

app = Flask(__name__)
users_controller = UsersController()

@app.route('/')
def index():

    # if you want to send a message to someone (must be registered to be able to receive message),
    # you have to use receptor public key to encrypt message

    # if a register user want to read his message, we must get all of his message from S3 buckets
    # and decrypt then using private key
    #private_key_plaintext = Encrypter.decrypt_private_key(cyphered_private_key)

    error = users_controller.register_user('test1', 'p1', 'test 1')

    return f"{error.value}"

if __name__ == '__main__':
    app.run()
