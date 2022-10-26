import decimal
import math
from typing import Any
from base64 import urlsafe_b64encode as b64encode, urlsafe_b64decode as b64decode
from django.db.models import BinaryField
from django import forms
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core import exceptions, validators

__all__ = [
    "VEncrypt",
    "FVEncrypt",
    "BinaryEncryptedField",
    "TextEncryptedField",
    "DecimalEncryptedField",
    "EmailEncryptedField",
]

KEY = settings.SECRET_KEY


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


class FVEncrypt:
    """Encrypt for Django Model Field"""

    __cipher = VEncrypt(KEY)

    def encrypt(self, data: str | int) -> bytes:
        return self.__cipher.encrypt(data)

    def decrypt(self, data: bytes) -> str:
        return self.__cipher.decrypt(data)


class BinaryEncryptedField(BinaryField, FVEncrypt):
    description = _("Base Encrypted Field")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value: Any) -> bytes:
        return self.encrypt(value)

    def from_db_value(self, value, expression, connection) -> str | None:
        if value is None:
            return value

        return self.decrypt(value)

    def to_python(self, value):
        if isinstance(value, str):
            return value

        return self.decrypt(value)


class EmailEncryptedField(BinaryEncryptedField):
    default_validators = [validators.validate_email]
    description = _("Email address")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        # As with CharField, this will cause email validation to be performed
        # twice.
        return super().formfield(
            **{
                "form_class": forms.EmailField,
                **kwargs,
            }
        )


class TextEncryptedField(BinaryEncryptedField):
    description = _("Text Encrypted Field")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                **({} if self.choices is not None else {"widget": forms.Textarea}),
                **kwargs,
            }
        )


class DecimalEncryptedField(BinaryEncryptedField):
    description = _("Decimal Encrypted Field")

    def __init__(
        self,
        verbose_name=None,
        name=None,
        max_digits=None,
        decimal_places=None,
        **kwargs,
    ):
        self.max_digits, self.decimal_places = max_digits, decimal_places
        super().__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.max_digits is not None:
            kwargs["max_digits"] = self.max_digits
        if self.decimal_places is not None:
            kwargs["decimal_places"] = self.decimal_places
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "max_digits": self.max_digits,
                "decimal_places": self.decimal_places,
                "form_class": forms.DecimalField,
                **kwargs,
            }
        )

    def get_prep_value(self, value: Any) -> bytes:
        return self.encrypt(str(value))

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value

        return decimal.Decimal(self.decrypt(value))

    def to_python(self, value):
        if value is None or isinstance(value, decimal.Decimal):
            return value
        elif isinstance(value, float):
            if math.isnan(value):
                raise exceptions.ValidationError(
                    self.error_messages["invalid"],
                    code="invalid",
                    params={"value": value},
                )
            return decimal.Decimal(value)

        return decimal.Decimal(self.decrypt(value))
