from django.urls import path

from .views import *


app_name = "core"

urlpatterns = [
    path("store/", GameListView.as_view(), name="store"),
    path("store/game/<slug:slug>/", GameDetailView.as_view(), name="store_game_detail"),
    path("cart/", CartView.as_view(), name="cart"),
    path("clear/", clear_session_view, name="clear"),
]
