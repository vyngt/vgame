from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


from .models import User
from .forms import VUserCreationForm, VUserChangeForm


class VUserAdmin(UserAdmin):
    form = VUserChangeForm
    add_form = VUserCreationForm
    model = User
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


admin.site.register(User, VUserAdmin)
