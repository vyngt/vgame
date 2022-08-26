from django.db import models
from django.utils.translation import gettext_lazy as _
from .utils import build_slug


def path_game_cover(instance: "Game", file_name: str) -> str:
    return f"{instance.name}/cover/{file_name}"


class Game(models.Model):
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"))
    price = models.DecimalField(_("price"), max_digits=4, decimal_places=2)
    cover = models.ImageField(
        _("cover"), upload_to=path_game_cover, default="default/cover.png"
    )
    slug = models.SlugField(_("slug"), max_length=130, unique=True)
    modified = models.DateTimeField(_("modified"), auto_now=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.pk:
            self.slug = build_slug(self.name, True)
        super().save(*args, **kwargs)
