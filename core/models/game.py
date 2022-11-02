from django.db import models
from django.utils.translation import gettext_lazy as _
from vaccount.models import User
from ..utils import build_slug
import encryption

__all__ = [
    "path_game_cover",
    "Game",
    "Library",
]


def path_game_cover(instance, file_name: str) -> str:
    return f"{instance.name}/cover/{file_name}"


class Game(models.Model):
    pk: int
    name = encryption.CharEncryptedField(_("name"))
    description = encryption.TextEncryptedField(_("description"))
    price = encryption.DecimalEncryptedField(_("price"), max_digits=4, decimal_places=2)
    cover = encryption.ImageEncryptedField(
        _("cover"), upload_to=path_game_cover, default="default/cover.png"
    )
    slug = encryption.SlugEncryptedField(_("slug"), unique=True)
    modified = encryption.DateTimeEncryptedField(_("modified"), auto_now=True)
    created = encryption.DateTimeEncryptedField(_("created"), auto_now_add=True)

    objects: models.Manager["Game"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.pk:
            self.slug = build_slug(self.name, True)
        super().save(*args, **kwargs)


class Library(models.Model):
    """Contain purchased items"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("user"))
    games = models.ManyToManyField(Game, verbose_name=_("games"), blank=True)

    def __str__(self) -> str:
        return f"Library {self.pk} | {self.user}"
