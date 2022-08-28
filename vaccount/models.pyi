from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from core.models import Library

class User(AbstractUser):
    """VGame User"""

    first_name: models.CharField[str, str]
    middle_name: models.CharField[str, str]
    last_name: models.CharField[str, str]
    email: models.EmailField[str, str]
    library: Library
    objects: UserManager["User"]
