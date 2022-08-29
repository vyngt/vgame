from django.urls import path

from .views import *

app_name = "checkout"

urlpatterns = [
    path("", CheckoutView.as_view(), name="main"),
    path("thankyou/", ThankYouView.as_view(), name="thankyou"),
    path("failed/", CheckoutFailView.as_view(), name="failed"),
]
