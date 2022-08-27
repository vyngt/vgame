from django.db import models
from django.utils.translation import gettext_lazy as _

from vaccount.models import User
from . import Game

__all__ = ["OrderDetail", "OrderItem"]

# class PaymentDetail(models.Model):
#     pass


class OrderDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"))
    modified = models.DateTimeField(_("modified"), auto_now=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    def __str__(self) -> str:
        return f"Order {self.pk} | User {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        OrderDetail, on_delete=models.CASCADE, verbose_name=_("order detail")
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name=_("game"))
    modified = models.DateTimeField(_("modified"), auto_now=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    def __str__(self) -> str:
        return f"Item {self.pk} | Order {self.order}"
