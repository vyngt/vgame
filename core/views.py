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
from .models import Game, Library, OrderDetail, OrderItem, PaymentDetail
from .utils import get_games_cart_query

__all__ = [
    "GameListView",
    "GameDetailView",
    "CartView",
    "CheckoutView",
    "CheckoutFailView",
    "ThankYouView",
]


def set_game_session(session: SessionBase, game: Game, action: str = "add"):
    """
    action: "add" | "remove"
    """
    games: list = session.get("games", [])
    total = Decimal(session.get("total", 0.0))
    if game not in games:
        if action == "add":
            games.append(game.pk)
            total += game.price
        elif action == "remove":
            games.remove(game.pk)
            total -= game.price
        session["games"] = games
        session["total"] = float("{:.2f}".format(total))


def clear_shopping_session(session: SessionBase):
    del session["total"]
    del session["games"]


class GameListView(View):
    def get(self, request: HttpRequest):
        games = Game.objects.all()
        context = {"games": games}
        return render(request, template_name="store/list.html", context=context)


class GameDetailView(View):
    def get(self, request: HttpRequest, slug: str):
        """Game's info"""
        game = Game.objects.get(slug=slug)
        context = {"game": game}
        return render(request, template_name="store/detail.html", context=context)

    def post(self, request: HttpRequest, slug: str):
        """Add to cart"""
        game = Game.objects.get(slug=slug)
        set_game_session(request.session, game, "add")
        return redirect("core:cart")


class CartView(View):
    def get(self, request: HttpRequest):
        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        games = Game.objects.filter(query) if query else None
        context = {
            "games": games,
            "total": request.session.get("total", 0.0),
        }
        return render(request, template_name="cart/cart.html", context=context)

    def post(self, request: HttpRequest):
        """Remove from cart"""
        game_id = request.POST.get("pk")
        game = Game.objects.get(pk=game_id)
        set_game_session(request.session, game, "remove")
        return JsonResponse({"ok": "removed"})


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

        return render(request, "cart/checkout.html", context=context)

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
            return redirect("core:failed")

        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        if not query:
            return redirect("core:failed")

        queryset = Game.objects.filter(query)
        _sum = queryset.aggregate(Sum("price"))
        amount = Decimal(str(round(_sum["price__sum"], 2)))

        order = self.create_order(request.user, self.create_payment(order_id, amount))
        order_items = self.fill_order_detail(queryset, order)
        self.add_to_user_library(request.user, order_items)
        clear_shopping_session(request.session)
        return redirect("core:thankyou")


class CheckoutFailView(TemplateView):
    template_name = "cart/failed.html"


class ThankYouView(TemplateView):
    template_name = "cart/thankyou.html"
