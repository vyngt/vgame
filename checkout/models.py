from django.db import models
from django.utils.translation import gettext_lazy as _

from vaccount.models import User
from core.models import Game
from core import encryption

__all__ = ["OrderDetail", "OrderItem", "PaymentDetail"]


class PaymentDetail(models.Model):
    order_id = encryption.BinaryEncryptedField(_("order id"), editable=True)
    amount = encryption.DecimalEncryptedField(
        _("amount"), max_digits=6, decimal_places=2, editable=True
    )  # type:ignore
    objects: models.Manager["PaymentDetail"]

    def __str__(self) -> str:
        return f"Payment {self.pk} | {self.order_id}"


class OrderDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"))
    payment = models.OneToOneField(
        PaymentDetail, on_delete=models.CASCADE, verbose_name=_("payment")
    )
    modified = models.DateTimeField(_("modified"), auto_now=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    objects: models.Manager["OrderDetail"]

    def __str__(self) -> str:
        return f"Order {self.pk} | User {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        OrderDetail, on_delete=models.CASCADE, verbose_name=_("order detail")
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name=_("game"))
    modified = models.DateTimeField(_("modified"), auto_now=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    objects: models.Manager["OrderItem"]

    def __str__(self) -> str:
        return f"Item {self.pk} | Order {self.order}"
