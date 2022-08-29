from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, QuerySet
from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse

from django.views.generic import TemplateView
from django.views import View

from decimal import Decimal
from vaccount.auth.http import AuthHttpRequest
from vaccount.models import User

from core.models import Game, Library, OrderDetail, OrderItem, PaymentDetail
from core.utils import get_games_cart_query, clear_shopping_session


# Create your views here.
__all__ = [
    "CheckoutView",
    "CheckoutFailView",
    "ThankYouView",
]


class CheckoutView(LoginRequiredMixin, View):
    # TODO: remove item that already belong to owner
    login_url = "account_login"

    def get(self, request: AuthHttpRequest):
        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        queryset = Game.objects.filter(query) if query else None
        _sum = queryset.aggregate(Sum("price")) if queryset else None
        context = {
            "key": settings.PAYPAL_CLIENT,
            "games": queryset,
            "count": queryset.count() if queryset else 0,
            "total": str(round(_sum["price__sum"], 2)) if _sum else "0.00",
        }

        return render(request, "checkout/checkout.html", context=context)

    def create_payment(self, order_id: str, amount: Decimal):
        return PaymentDetail.objects.create(order_id=order_id, amount=amount)

    def create_order(self, user: User, payment: PaymentDetail):
        return OrderDetail.objects.create(user=user, payment=payment)

    def fill_order_detail(
        self, games_queryset: QuerySet[Game], order_detail: OrderDetail
    ):
        items: list[OrderItem] = []
        for game in games_queryset:
            items.append(OrderItem(order=order_detail, game=game))

        return OrderItem.objects.bulk_create(items)

    def add_to_user_library(self, user: User, items: list[OrderItem]):
        for item in items:
            user.library.games.add(item.game)

    def post(self, request: AuthHttpRequest):
        order_id = request.POST.get("order_id")
        if not order_id:
            return redirect("checkout:failed")

        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        if not query:
            return redirect("checkout:failed")

        queryset = Game.objects.filter(query)
        _sum = queryset.aggregate(Sum("price"))
        amount = Decimal(str(round(_sum["price__sum"], 2)))

        order = self.create_order(request.user, self.create_payment(order_id, amount))
        order_items = self.fill_order_detail(queryset, order)
        self.add_to_user_library(request.user, order_items)
        clear_shopping_session(request.session)
        return redirect("checkout:thankyou")


class CheckoutFailView(TemplateView):
    template_name = "checkout/failed.html"


class ThankYouView(TemplateView):
    template_name = "checkout/thankyou.html"
