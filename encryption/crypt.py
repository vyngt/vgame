from base64 import urlsafe_b64encode as b64encode, urlsafe_b64decode as b64decode
from django.conf import settings
import abc

__all__ = ["VEncrypt"]

KEY = settings.SECRET_KEY


class _VEncrypt:
    """Base Encrypt"""

    def __init__(self, key: str):
        self.key = key

    def encrypt(self, data: str | int) -> bytes:
        enc = ""
        for i, c in enumerate(str(data)):
            key_c = self.key[i % len(self.key)]
            enc += chr(ord(c) + ord(key_c) % 256)

        return b64encode(enc.encode())

    def decrypt(self, data: bytes) -> str:
        original = ""
        for i, c in enumerate(b64decode(data).decode()):
            key_c = self.key[i % len(self.key)]
            original += chr(ord(c) - ord(key_c) % 256)

        return original


class VEncrypt:
    """Abstract"""

    __cipher = _VEncrypt(KEY)

    def encrypt(self, data: str | int) -> bytes:
        return self.__cipher.encrypt(data)

    def decrypt(self, data: bytes) -> str:
        return self.__cipher.decrypt(data)
