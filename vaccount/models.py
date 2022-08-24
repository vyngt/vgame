from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.db import models


class User(AbstractUser):
    """VGame User"""

    middle_name = models.CharField(_("middle name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"))

    objects: UserManager["User"]

    def get_full_name(self):
        full_name = "%s %s %s" % (self.last_name, self.middle_name, self.first_name)
        return full_name.strip()
