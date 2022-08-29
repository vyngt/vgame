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
    # Store
    "GameListView",
    "GameDetailView",
    "CartView",
    # User Library
    "LibraryView",
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


class LibraryView(LoginRequiredMixin, View):
    pass
