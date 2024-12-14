import boto3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

KMS_KEY = "8c1a2230-aa09-4624-8d45-0d9a0be3aefa"
kms_client = boto3.client("kms", region_name="eu-central-1")

class Encrypter:
    def __init__(self):
        pass

    @staticmethod
    def generate_key_pair():
        keys = kms_client.generate_data_key_pair_without_plaintext(KeyId=KMS_KEY, KeyPairSpec="RSA_2048")

        # keys["PrivateKeyCiphertextBlob"] is the cyphered private key
        # keys["PublicKey"] is the public key
        return keys["PublicKey"], keys["PrivateKeyCiphertextBlob"]

    @staticmethod
    def encrypt_password(password, public_key):
        """
        Encrypt password with public key

        :param password: plaintext password
        :param public_key: public key from database
        :return: password encrypted
        """
        public_key = RSA.import_key(public_key)
        # Return a cipher object PKCS1OAEP_Cipher
        # that can be used to perform PKCS#1 OAEP encryption or decryption.
        cipher = PKCS1_OAEP.new(public_key)
        #Encodes the string, using the specified encoding.
        encoded_data = password.encode("utf-8")
        # Encrypt a password with PKCS#1 OAEP.
        return cipher.encrypt(encoded_data)

    @staticmethod
    def decrypt_password(password, private_key):
        """
        Decrypt password with private key from database.
        This function decrypt private key into plaintext.

        :param password: encrypted password
        :param private_key: private key from database. Will be decrypted here
        :return: password decrypted in plaintext
        """
        private_key = RSA.import_key(Encrypter.__decrypt_private_key(private_key))
        # Return a cipher object PKCS1OAEP_Cipher
        # that can be used to perform PKCS#1 OAEP encryption or decryption.
        cipher = PKCS1_OAEP.new(private_key)
        # Encrypt a message with PKCS#1 OAEP.
        decrypted_data = cipher.decrypt(password)
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