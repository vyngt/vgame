from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View

from vaccount.auth.http import AuthHttpRequest
from core.models import Game
from core.utils import get_games_cart_query

from .utils import generate_paypal_client_token

# Create your views here.
__all__ = [
    "CheckoutView",
    "CheckoutFailView",
    "ThankYouView",
]


class CheckoutFailView(TemplateView):
    template_name = "checkout/failed.html"


class ThankYouView(TemplateView):
    template_name = "checkout/thankyou.html"


class CheckoutView(LoginRequiredMixin, View):
    login_url = "account_login"

    paypal_client: str = settings.PAYPAL_CLIENT

    def get(self, request: AuthHttpRequest):
        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        queryset = Game.objects.filter(query) if query else None
        _sum = queryset.aggregate(Sum("price")) if queryset else None

        client_id = self.paypal_client
        client_token = generate_paypal_client_token()

        context = {
            "client_id": client_id,
            "client_token": client_token,
            "games": queryset,
            "count": queryset.count() if queryset else 0,
            "total": str(round(_sum["price__sum"], 2)) if _sum else "0.00",
        }
        return render(request, "checkout/index.html", context=context)


# TODO: Loại bỏ những item đã mua rồi trong quá trình thanh toán.
