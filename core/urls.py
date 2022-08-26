from django.urls import path

from .views import *


app_name = "core"

urlpatterns = [
    path("", GameList.as_view(), name="game_list"),
]
