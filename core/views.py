from django.shortcuts import render
from django.views import View
from .models import Game

__all__ = ["GameList"]


class GameList(View):
    def get(self, request):
        games = Game.objects.all()
        context = {"games": games}
        return render(request, template_name="game/list.html", context=context)
