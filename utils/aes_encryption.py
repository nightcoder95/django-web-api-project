import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.conf import settings

BLOCK_SIZE = 16  # AES block size

def get_key_iv():
    key = settings.AES_SECRET_KEY.encode('utf-8')
    iv = settings.AES_SECRET_IV.encode('utf-8')
    return key, iv

def encrypt_aes(data: str) -> str:
    key, iv = get_key_iv()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data.encode(), BLOCK_SIZE))
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt_aes(encrypted_str: str) -> str:
    key, iv = get_key_iv()
    encrypted_bytes = base64.b64decode(encrypted_str)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted_bytes), BLOCK_SIZE)
    return decrypted.decode('utf-8')
