from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from core import encryption


class User(AbstractUser):
    """VGame User"""

    username_validator = UnicodeUsernameValidator()

    username = encryption.BinaryEncryptedField(
        _("username"),
        unique=True,
        editable=True,
        help_text=_("Required. Letters, digits and @/./+/-/_ only."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = encryption.BinaryEncryptedField(
        _("first name"), editable=True, blank=True
    )
    middle_name = encryption.BinaryEncryptedField(
        _("middle name"), editable=True, blank=True
    )
    last_name = encryption.BinaryEncryptedField(
        _("last name"), editable=True, blank=True
    )
    email = encryption.EmailEncryptedField(
        _("email address"), editable=True, blank=True
    )

    objects: UserManager["User"]

    def get_full_name(self):
        full_name = "%s %s %s" % (self.last_name, self.middle_name, self.first_name)
        return full_name.strip()
