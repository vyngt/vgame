from django.contrib.sessions.backends.base import SessionBase
from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.views import View

from decimal import Decimal
from .models import Game
from .utils import get_games_cart_query

__all__ = ["GameListView", "GameDetailView", "CartView", "clear_session_view"]


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


def clear_session_view(request: HttpRequest):
    request.session.clear()
    return redirect("core:cart")


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
        print(request.session)
        return redirect("core:cart")


class CartView(View):
    def get(self, request: HttpRequest):
        context = {}

        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        games = Game.objects.filter(query) if query else None
        context["games"] = games
        context["total"] = request.session.get("total", 0.0)
        return render(request, template_name="cart/cart.html", context=context)

    def post(self, request: HttpRequest):
        """Remove from cart"""
        print(request.POST)
        game_id = request.POST.get("pk")
        game = Game.objects.get(pk=game_id)
        set_game_session(request.session, game, "remove")
        print(request.session["games"])
        return JsonResponse({"ok": "removed"})


class CheckoutView(View):
    pass
