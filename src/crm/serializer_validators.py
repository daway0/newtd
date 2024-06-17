import re
from typing import Literal

from rest_framework.serializers import ValidationError


def gender(g: Literal["M", "F"]) -> str:
    if g.upper() not in ("M", "F"):
        raise ValidationError({"error": "invalid gender."})

    return g


def national_code(n: str) -> str:
    if len(n) != 10 or not n.isdigit():
        raise ValidationError({"error": "invalid national code."})

    return n


def phone_number(n: str) -> str:
    if not n.isdigit():
        raise ValidationError({"error": "invalid phone number."})

    return n


def date(d: str) -> str:
    if not re.match(r"^\d{4}\/(0[1-9]|1[1-2])\/(0[1-9]|[1-2]\d|3[01])$", d):
        raise ValidationError({"error": "invalid date."})

    return d


def card_number(cn: str) -> str:
    if not cn.isdigit() or len(cn) != 16:
        raise ValidationError({"error": "invalid card number."})

    return cn
