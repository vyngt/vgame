from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Library
from .models import User


@receiver(post_save, sender=User)
def init_library(sender, instance: User, created: bool, **kwargs):
    if created:
        Library.objects.create(user=instance)
