import base64
import requests
from django.conf import settings

__all__ = ["generate_paypal_access_token", "generate_paypal_client_token"]

paypal_api_url = settings.PAYPAL_API_URL


def generate_paypal_access_token() -> str:
    client = settings.PAYPAL_CLIENT
    secret = settings.PAYPAL_SECRET
    url = f"{paypal_api_url}/v1/oauth2/token"
    authtoken = base64.b64encode(f"{client}:{secret}".encode()).decode()
    headers = {"Authorization": f"Basic {authtoken}"}
    response = requests.post(
        url=url, data={"grant_type": "client_credentials"}, headers=headers
    )
    return response.json()["access_token"]


def generate_paypal_client_token() -> str:
    access_token = generate_paypal_access_token()
    url = f"{paypal_api_url}/v1/identity/generate-token"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept-Language": "en_US",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers)
    return response.json()["client_token"]
