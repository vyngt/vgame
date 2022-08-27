from django.contrib.sessions.backends.base import SessionBase
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.views import View

from .models import Game
from .utils import get_games_cart_query

__all__ = ["GameListView", "GameDetailView", "CartView", "clear_session_view"]


def set_game_session(session: SessionBase, game: Game):
    games: list = session.get("games", [])
    if game not in games:
        games.append(game.pk)
        session["games"] = games


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
        set_game_session(request.session, game)
        print(request.session)
        return redirect("core:cart")


class CartView(View):
    def get(self, request: HttpRequest):
        context = {}

        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        games = Game.objects.filter(query) if query else None
        context["games"] = games
        return render(request, template_name="cart/cart.html", context=context)

    def delete(self, request: HttpRequest):
        return HttpResponse("Deleted")


class CheckoutView(View):
    pass
