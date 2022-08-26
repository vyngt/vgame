from django.forms import ModelForm

from .models import Game

__all__ = ["GameAdminForm"]


class GameAdminForm(ModelForm):
    class Meta:
        model = Game
        exclude = ["slug", "created", "modified"]
