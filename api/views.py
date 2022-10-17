import requests
import stripe
from typing import Any
from django.conf import settings
from django.db.models import Sum, QuerySet

from rest_framework.views import APIView
from rest_framework.response import Response

from vaccount.auth.http import AuthHttpRequest
from vaccount.models import User

from core.utils import get_games_cart_query, clear_shopping_session
from core.models import Game

from checkout.utils import generate_paypal_access_token
from checkout.models import OrderDetail, OrderItem, PaymentDetail

from decimal import Decimal

__all__ = ["CreateOrder", "CapturePayment", "StripeIntentPayment"]


class CreateOrder(APIView):
    def create_order(self, request: AuthHttpRequest):
        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        assert query
        queryset = Game.objects.filter(query)
        _sum = queryset.aggregate(Sum("price"))
        amount = str(round(_sum["price__sum"], 2))

        access_token = generate_paypal_access_token()
        url = f"{settings.PAYPAL_API_URL}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        json_data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "USD",
                        "value": amount,
                    },
                },
            ],
        }
        response = requests.post(url, headers=headers, json=json_data)
        return response.json()

    def post(self, request: AuthHttpRequest):
        data = self.create_order(request)
        return Response(data)


class CapturePayment(APIView):
    def capture_payment(self, order_id: str):
        access_token = generate_paypal_access_token()
        url = f"{settings.PAYPAL_API_URL}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.post(url, headers=headers)
        return response.json()

    def save_payment(self, order_id: str, amount: Decimal):
        return PaymentDetail.objects.create(order_id=order_id, amount=amount)

    def save_order(self, user: User, payment: PaymentDetail):
        return OrderDetail.objects.create(user=user, payment=payment)

    def save_order_items(
        self, games_queryset: QuerySet[Game], order_detail: OrderDetail
    ):
        items: list[OrderItem] = []
        for game in games_queryset:
            items.append(OrderItem(order=order_detail, game=game))
        return OrderItem.objects.bulk_create(items)

    def add_game_to_user_library(self, user: User, items: list[OrderItem]):
        for item in items:
            user.library.games.add(item.game)

    def perform_post_checkout(self, request: AuthHttpRequest, data: Any):
        # Setup
        transaction_id = data["id"]
        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        assert query
        queryset = Game.objects.filter(query)
        amount = Decimal(
            data["purchase_units"][0]["payments"]["captures"][0]["amount"]["value"]
        )
        # Perform
        payment = self.save_payment(transaction_id, amount)
        order = self.save_order(request.user, payment)
        order_items = self.save_order_items(queryset, order)
        self.add_game_to_user_library(request.user, order_items)
        clear_shopping_session(request.session)

    def post(self, request: AuthHttpRequest, order_id: str):

        data = self.capture_payment(order_id)
        if data["status"] == "COMPLETED":
            self.perform_post_checkout(request, data)
        return Response(data)


# Stripe
# https://stripe.com/docs/payments/quickstart
class StripeIntentPayment(APIView):
    def calculate_amount(self, request: AuthHttpRequest):
        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        assert query
        queryset = Game.objects.filter(query)
        _sum = queryset.aggregate(Sum("price"))
        amount = str(round(_sum["price__sum"], 2))
        return int(float(amount) * 100)

    def post(self, request: AuthHttpRequest):
        try:
            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                api_key=settings.STRIPE_SECRET,
                amount=self.calculate_amount(request),
                currency="usd",
                automatic_payment_methods={
                    "enabled": True,
                },
            )
            return Response({"clientSecret": intent["client_secret"]})
        except Exception as e:
            return Response(status=403)


class PostStripeIntentPayment(CapturePayment):
    def post(self, request: AuthHttpRequest, client: str):
        intent = stripe.PaymentIntent.retrieve(
            id=client, api_key=settings.STRIPE_SECRET
        )
        games_session: list[int] | None = request.session.get("games")
        query = get_games_cart_query(games_session)
        assert query
        queryset = Game.objects.filter(query)
        payment = self.save_payment(client, Decimal(str(intent["amount"] / 100)))
        order = self.save_order(request.user, payment)
        order_items = self.save_order_items(queryset, order)
        self.add_game_to_user_library(request.user, order_items)
        clear_shopping_session(request.session)

        return Response({"ok": 1})
