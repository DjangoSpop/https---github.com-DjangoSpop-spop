# utils/encryption.py
from cryptography.fernet import Fernet
from django.conf import settings
import base64

def encrypt_file(file_content):
    key = settings.ENCRYPTION_KEY
    f = Fernet(key)
    encrypted_data = f.encrypt(file_content)
    return encrypted_data

def decrypt_file(encrypted_content):
    key = settings.ENCRYPTION_KEY
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_content)
    return decrypted_data