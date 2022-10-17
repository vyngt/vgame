from django.urls import path
from .views import *
from .views import PostStripeIntentPayment

app_name = "api"

urlpatterns = [
    path("orders/", CreateOrder.as_view(), name="create_order"),
    path("orders/<order_id>/capture/", CapturePayment.as_view(), name="create_order"),
    path("orders/stripe/", StripeIntentPayment.as_view(), name="stripe_create_order"),
    path(
        "orders/stripe/<client>/",
        PostStripeIntentPayment.as_view(),
        name="post_stripe_payment",
    ),
]
