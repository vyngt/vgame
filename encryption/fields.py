import decimal
from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _
from django import forms
from django.core import checks, exceptions, validators

from .mixins import EncryptionMixin

__all__ = [
    "BaseEncryptionField",
    "CharEncryptedField",
    "TextEncryptedField",
    "SlugEncryptedField",
    "EmailEncryptedField",
    "DecimalEncryptedField",
    "ImageEncryptedField",
    "DateEncryptedField",
    "DateTimeEncryptedField",
]


class BaseEncryptionField(EncryptionMixin, models.Field):
    description = _("String to Binary Data")
    empty_values = [None, ""]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.max_length is not None:
            self.validators.append(validators.MaxLengthValidator(self.max_length))

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def get_placeholder(self, value, compiler, connection):
        return connection.ops.binary_placeholder_sql(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super().get_db_prep_value(value, connection, prepared)
        if value is not None:
            return connection.Database.Binary(value)
        return value

    def get_default(self):
        if self.has_default() and not callable(self.default):
            return self.default
        default = super().get_default()
        if default == "":
            return ""
        return default


class CharEncryptedField(BaseEncryptionField):
    pass


class TextEncryptedField(BaseEncryptionField):
    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "max_length": self.max_length,
                **({} if self.choices is not None else {"widget": forms.Textarea}),
                **kwargs,
            }
        )


class EmailEncryptedField(BaseEncryptionField):
    default_validators = [validators.validate_email]

    def formfield(self, **kwargs):
        # As with CharField, this will cause email validation to be performed
        # twice.
        return super().formfield(
            **{
                "form_class": forms.EmailField,
                **kwargs,
            }
        )


class SlugEncryptedField(EncryptionMixin, models.SlugField):
    def __init__(self, *args, allow_unicode=False, **kwargs):
        self.allow_unicode = allow_unicode
        if self.allow_unicode:
            self.default_validators = [validators.validate_unicode_slug]
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.allow_unicode is not False:
            kwargs["allow_unicode"] = self.allow_unicode
        return name, path, args, kwargs


class DecimalEncryptedField(EncryptionMixin, models.DecimalField):
    def get_db_prep_save(self, value: Any, connection: Any) -> Any:
        return self.get_db_prep_value(value, connection, False)

    def from_db_value(self, value, expression, connection):
        value = super().from_db_value(value, expression, connection)
        if not value:
            return value
        return decimal.Decimal(value)


class ImageEncryptedField(EncryptionMixin, models.ImageField):
    pass


class DateEncryptedField(EncryptionMixin, models.DateField):
    def get_db_prep_value(self, value: Any, connection: Any, prepared: bool) -> Any:
        return super().get_db_prep_value(value, connection, prepared)


class DateTimeEncryptedField(EncryptionMixin, models.DateTimeField):
    def get_db_prep_value(self, value: Any, connection: Any, prepared: bool) -> Any:
        return super().get_db_prep_value(value, connection, prepared)


class BooleanEncryptedField(EncryptionMixin, models.BooleanField):
    # TODO
    pass
