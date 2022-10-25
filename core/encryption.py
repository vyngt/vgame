from typing import Any
from base64 import urlsafe_b64encode as b64encode, urlsafe_b64decode as b64decode
from django.db.models import Field, BinaryField
from django.utils.translation import gettext_lazy as _
from django.conf import settings

__all__ = ["VEncrypt", "DVEncrypt", "BinaryEncryptedField"]


class VEncrypt:
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


class DVEncrypt:
    """Encrypt for Django App"""

    __key = settings.SECRET_KEY
    __cipher = VEncrypt(__key)

    def encrypt(self, data: str | int) -> bytes:
        return self.__cipher.encrypt(data)

    def decrypt(self, data: bytes) -> str:
        return self.__cipher.decrypt(data)


class BinaryEncryptedField(BinaryField):
    description = _("Base Encrypted Field")
    __cipher = DVEncrypt()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value: Any) -> bytes:
        return self.__cipher.encrypt(value)

    def from_db_value(self, value, expression, connection) -> str | None:
        if value is None:
            return value

        return self.__cipher.decrypt(value)

    def to_python(self, value):
        if isinstance(value, str):
            return value

        return self.__cipher.decrypt(value)
