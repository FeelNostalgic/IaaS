from flask import Flask
from Backend.encrypter import Encrypter

app = Flask(__name__)
encrypter = Encrypter()

@app.route('/')
def index():

    # if you want to send a message to someone (must be registered to be able to receive message),
    # you have to use receptor public key to encrypt message

    # if a register user want to read his message, we must get all of his message from S3 buckets
    # and decrypt then using private key
    #private_key_plaintext = Encrypter.decrypt_private_key(cyphered_private_key)

    return "Hello World!"


if __name__ == '__main__':
    app.run()
