from datetime import datetime
from django.utils.text import slugify
from django.db.models import Q

__all__ = ["build_slug", "get_games_cart_query"]


def build_slug(text: str, auto_now: bool = False, allow_unicode: bool = False) -> str:
    sub_text = ""
    if auto_now:
        sub_text = datetime.now().strftime("%d%m%Y%H%M%S")
    slug = slugify(" ".join([text, sub_text]).strip(), allow_unicode)
    return slug


def get_games_cart_query(games: list[int] | None):
    query: None | Q = None
    if games:
        for game in games:
            if query is None:
                query = Q(pk=game)
            else:
                query |= Q(pk=game)

    return query
