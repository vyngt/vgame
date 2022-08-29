from django.urls import path

from .views import *


app_name = "core"

urlpatterns = [
    path("store/", GameListView.as_view(), name="store"),
    path("store/game/<slug:slug>/", GameDetailView.as_view(), name="store_game_detail"),
    path("cart/", CartView.as_view(), name="cart"),
    path("library/", LibraryView.as_view(), name="library"),
    path("order-history/", OrderHistoryView.as_view(), name="order_history"),
]
