import base64
from decimal import Decimal
import requests
import braintree
from django.conf import settings
from django.db.models import QuerySet
from core.models import Game

__all__ = [
    "generate_paypal_access_token",
    "generate_paypal_client_token",
    "get_games_sum_price",
    "DBrainTree",
]


class DBrainTree:
    def __init__(self):
        environment = braintree.Environment.Sandbox  # type:ignore
        if not settings.PAYMENTS["braintree"]["sandbox"]:
            environment = braintree.Environment.Production  # type:ignore
        self.gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=environment, **settings.PAYMENTS["braintree"]["config"]
            )
        )

    def generate_token(self):
        return self.gateway.client_token.generate()

    def transact(self, options):
        return self.gateway.transaction.sale(options)  # type: ignore

    def find_transaction(self, transaction_id):
        return self.gateway.transaction.find(transaction_id)  # type: ignore


def generate_paypal_access_token() -> str:
    client = settings.PAYMENTS["paypal"]["client_key"]
    secret = settings.PAYMENTS["paypal"]["secret_key"]
    url = f"{settings.PAYMENTS['paypal']['api_url']}/v1/oauth2/token"
    authtoken = base64.b64encode(f"{client}:{secret}".encode()).decode()
    headers = {"Authorization": f"Basic {authtoken}"}
    response = requests.post(
        url=url, data={"grant_type": "client_credentials"}, headers=headers
    )
    return response.json()["access_token"]


def generate_paypal_client_token() -> str:
    access_token = generate_paypal_access_token()
    url = f"{settings.PAYMENTS['paypal']['api_url']}/v1/identity/generate-token"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept-Language": "en_US",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers)
    return response.json()["client_token"]


def get_games_sum_price(queryset: QuerySet[Game]) -> float:
    return float(sum(game.price for game in queryset))
