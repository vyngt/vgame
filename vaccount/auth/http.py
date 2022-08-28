from django.http import HttpRequest
from ..models import User


class AuthHttpRequest(HttpRequest):
    user: User
