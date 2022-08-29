from django.urls import path
from .views import *

app_name = "api"

urlpatterns = [
    path("orders/", CreateOrder.as_view(), name="create_order"),
    path("orders/<order_id>/capture/", CapturePayment.as_view(), name="create_order"),
]
