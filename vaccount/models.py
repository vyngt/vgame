from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
import encryption


class User(AbstractUser):
    """VGame User"""

    username_validator = UnicodeUsernameValidator()

    username = encryption.CharEncryptedField(
        _("username"),
        unique=True,
        help_text=_("Required. Letters, digits and @/./+/-/_ only."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = encryption.CharEncryptedField(_("first name"), blank=True)
    middle_name = encryption.CharEncryptedField(_("middle name"), blank=True)
    last_name = encryption.CharEncryptedField(_("last name"), blank=True)
    email = encryption.EmailEncryptedField(_("email address"), blank=True)

    objects: UserManager["User"]

    def get_full_name(self):
        full_name = "%s %s %s" % (self.last_name, self.middle_name, self.first_name)
        return full_name.strip()
