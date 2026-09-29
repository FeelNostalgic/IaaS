import boto3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes

from Backend.config import AWS_KMS_KEY_ID, AWS_REGION

kms_client = boto3.client("kms", region_name=AWS_REGION)

class Encrypter:
    def __init__(self):
        pass

    @staticmethod
    def generate_key_pair():
        keys = kms_client.generate_data_key_pair_without_plaintext(KeyId=AWS_KMS_KEY_ID, KeyPairSpec="RSA_2048")

        # keys["PrivateKeyCiphertextBlob"] is the cyphered private key
        # keys["PublicKey"] is the public key
        return keys["PublicKey"], keys["PrivateKeyCiphertextBlob"]

    @staticmethod
    def encrypt_data(data, public_key):
        """
        Encrypt data with public key

        :param data: plaintext data
        :param public_key: public key from database
        :return: data encrypted
        """
        public_key = RSA.import_key(public_key)
        # Return a cipher object PKCS1OAEP_Cipher
        # that can be used to perform PKCS#1 OAEP encryption or decryption.
        cipher = PKCS1_OAEP.new(public_key)
        #Encodes the string, using the specified encoding.
        encoded_data = data.encode("utf-8")
        # Encrypt a password with PKCS#1 OAEP.
        return cipher.encrypt(encoded_data)

    @staticmethod
    def decrypt_data(data, private_key):
        """
        Decrypt data with private key from database.
        This function decrypt private key into plaintext.

        :param data: encrypted data
        :param private_key: private key from database. Will be decrypted here
        :return: data decrypted in plaintext
        """
        decrypted_private_key = Encrypter.__decrypt_private_key(private_key)
        private_key = RSA.import_key(decrypted_private_key)
        # Return a cipher object PKCS1OAEP_Cipher
        # that can be used to perform PKCS#1 OAEP encryption or decryption.
        cipher = PKCS1_OAEP.new(private_key)
        # Encrypt a message with PKCS#1 OAEP.
        decrypted_data = cipher.decrypt(data)
        # Decodes the bytes-like object using the specified encoding.
        return decrypted_data.decode("utf-8")

    @staticmethod
    def __decrypt_private_key(cyphered_private_key):
        """
        Decrypts a private key encrypted by AWS KMS.
        This function interacts with the AWS Key Management Service (KMS) to decrypt
        an encrypted private key provided as a ciphertext blob.
    
        :param cyphered_private_key: The encrypted private key, retrieved from KMS generate_data_key_pair.
        :return: The decrypted private key in plaintext, as plaintext.
        """
        decrypt_response = kms_client.decrypt(CiphertextBlob=cyphered_private_key)
        return decrypt_response["Plaintext"]

    @staticmethod
    def encrypt_large_data(data, public_key):
        """
        Encrypt data using a hybrid AES+RSA approach.
    
        :param data: plaintext data (string)
        :param public_key: public key from database (string or bytes)
        :return: a dictionary containing the encrypted AES key, nonce, tag, and encrypted_message
        """
        # Import the RSA public key
        public_key = RSA.import_key(public_key)

        # Generate a random AES key
        aes_key = get_random_bytes(16)  # 16 bytes = 128-bit AES key

        # Encrypt the data with AES
        cipher_aes = AES.new(aes_key, AES.MODE_EAX)
        nonce = cipher_aes.nonce
        encrypted_message, tag = cipher_aes.encrypt_and_digest(data.encode("utf-8"))

        # Encrypt the AES key with RSA
        cipher_rsa = PKCS1_OAEP.new(public_key)
        encrypted_aes_key = cipher_rsa.encrypt(aes_key)

        # Return the encrypted components as a dictionary
        return {
            "encrypted_aes_key": encrypted_aes_key,
            "nonce": nonce,
            "tag":tag,
            "encrypted_message": encrypted_message
        }

    @staticmethod
    def decrypt_large_data(encrypted_data, private_key):
        """
        Decrypt data using a hybrid AES+RSA approach.

        :param encrypted_data: a dictionary containing encrypted AES key, nonce, tag, and encrypted_message
        :param private_key: private RSA key for decryption (string or bytes)
        :return: decrypted plaintext data (string)
        """
        # Import the RSA private key
        decrypted_private_key = Encrypter.__decrypt_private_key(private_key)
        private_key = RSA.import_key(decrypted_private_key)

        # Decode and decrypt the AES key using RSA
        cipher_rsa = PKCS1_OAEP.new(private_key)
        encrypted_aes_key = encrypted_data["encrypted_aes_key"]
        aes_key = cipher_rsa.decrypt(encrypted_aes_key)

        # Decode the AES components
        nonce =encrypted_data["nonce"]
        tag = encrypted_data["tag"]
        encrypted_message = encrypted_data["encrypted_message"]

        # Decrypt the data using AES
        cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher_aes.decrypt_and_verify(encrypted_message, tag)

        # Return the plaintext data as a string
        return plaintext.decode("utf-8")