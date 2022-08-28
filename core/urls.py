from django.urls import path

from .views import *


app_name = "core"

urlpatterns = [
    path("store/", GameListView.as_view(), name="store"),
    path("store/game/<slug:slug>/", GameDetailView.as_view(), name="store_game_detail"),
    path("cart/", CartView.as_view(), name="cart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("checkout/thankyou/", ThankYouView.as_view(), name="thankyou"),
    path("checkout/failed/", CheckoutFailView.as_view(), name="failed"),
]
