from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import *
from .forms import GameAdminForm


class GameAdmin(admin.ModelAdmin):
    form = GameAdminForm
    fieldsets = [
        (
            _("Game Information"),
            {"fields": ["name", "description", "cover"]},
        ),
        (
            _("Sell"),
            {"fields": ["price"]},
        ),
        (
            _("Addition"),
            {"fields": ["slug", "created", "modified"]},
        ),
    ]
    list_display = (
        "name",
        "created",
        "modified",
    )
    search_fields = ("name",)
    readonly_fields = ("slug", "created", "modified")


# class JustFunAdmin(admin.ModelAdmin):


admin.site.register(Game, GameAdmin)
admin.site.register(Library)
admin.site.register(JustFun)
