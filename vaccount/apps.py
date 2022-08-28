from django.apps import AppConfig


class VAccountConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "vaccount"

    def ready(self) -> None:
        from . import signals
