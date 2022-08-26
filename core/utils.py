from datetime import datetime
from django.utils.text import slugify


def build_slug(text: str, auto_now: bool = False, allow_unicode: bool = False) -> str:
    sub_text = ""
    if auto_now:
        sub_text = datetime.now().strftime("%d%m%Y%H%M%S")
    slug = slugify(" ".join([text, sub_text]).strip(), allow_unicode)
    return slug
