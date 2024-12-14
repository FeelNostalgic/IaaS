import boto3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes

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
        Cifra datos largos utilizando un enfoque híbrido: RSA + AES.

        :param data: Texto plano a cifrar.
        :param public_key: Clave pública RSA.
        :return: Tuple (clave_aes_cifrada, datos_cifrados, iv)
        """
        # Cargar clave pública RSA
        public_key = RSA.import_key(public_key)
        rsa_cipher = PKCS1_OAEP.new(public_key)

        # Generar una clave simétrica AES (clave de sesión)
        aes_key = get_random_bytes(16)  # Genera una clave AES de 128 bits

        # Cifrar los datos largos con AES en modo CBC
        cipher_aes = AES.new(aes_key, AES.MODE_CBC)  # Cifrado AES con modo CBC
        iv = cipher_aes.iv  # Vector de inicialización (IV)
        data_padded = Encrypter.__pad_data(data.encode("utf-8"))  # Asegúrate de ajustar el texto (padding)
        encrypted_data = cipher_aes.encrypt(data_padded)

        # Cifrar la clave AES con RSA
        encrypted_aes_key = rsa_cipher.encrypt(aes_key)

        return encrypted_aes_key, encrypted_data, iv

    @staticmethod
    def __pad_data(data):
        """
        Aplica relleno (padding) para que los datos sean múltiplos del tamaño del bloque AES (16 bytes).
        """
        block_size = 16
        padding_length = block_size - len(data) % block_size
        return data + bytes([padding_length]) * padding_length

    @staticmethod
    def decrypt_large_data(encrypted_aes_key, encrypted_data, iv, encrypted_private_key):
        """
        Descifra datos largos utilizando un enfoque híbrido: RSA + AES.

        :param encrypted_aes_key: Clave AES cifrada con RSA.
        :param encrypted_data: Datos cifrados con AES.
        :param iv: Vector de inicialización (IV) usado para AES.
        :param encrypted_private_key: Clave privada RSA.
        :return: Texto descifrado.
        """
        # Cargar clave privada RSA
        decrypted_private_key = Encrypter.__decrypt_private_key(encrypted_private_key)
        private_key = RSA.import_key(decrypted_private_key)
        rsa_cipher = PKCS1_OAEP.new(private_key)

        # Descifrar la clave AES con RSA
        aes_key = rsa_cipher.decrypt(encrypted_aes_key)

        # Descifrar los datos largos con AES en modo CBC
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
        data_padded = cipher_aes.decrypt(encrypted_data)
        return Encrypter.__unpad_data(data_padded)

    @staticmethod
    def __unpad_data(data):
        """
        Elimina el relleno (padding) de los datos descifrados.
        """
        padding_length = data[-1]
        return data[:-padding_length]