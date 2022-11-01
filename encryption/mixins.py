from typing import Any
from .crypt import VEncrypt


class EncryptionMixin(VEncrypt):
    def get_internal_type(self) -> str:
        return "BinaryField"

    def get_prep_value(self, value: Any) -> bytes:
        return self.encrypt(value)

    def from_db_value(self, value, expression, connection):
        if value is None or not value:
            return value
        return self.decrypt(value)
