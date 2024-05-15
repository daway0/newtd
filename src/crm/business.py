from functools import wraps
from typing import Callable

from . import validators
from .models import People, PeopleDetailedInfo, PeopleDetailTypeChoices


class Info:
    """
    Class for add/remove/editing people's infos.
    """

    def __init__(self, info: str, type: PeopleDetailTypeChoices.names) -> None:
        """
        Args:
            'info': The info which you want to modify / add.
            'type': Type of info you are modifing / adding, choose from
                PeopleDetailTypeChoices enum consts.
        """

        self.info = info
        self.type = type
        self.model: PeopleDetailedInfo = None

    def fetch_model_required(func: Callable):
        """
        Some methods need to access current info obj in order to
        do some operations like delete or change,
        thus we need to fetch the obj for them.

        Use this decorator for those methods.
        """

        @wraps(func)
        def wrapper(self: "Info", *args, **kwargs):
            if self.model is None:
                self.fetch_model()

            return func(self, *args, **kwargs)

        return wrapper

    def fetch_model(self):
        """
        Raises:
            'ValueError': if info does not exists on db.
        """

        model = PeopleDetailedInfo.objects.filter(
            detail_type=self.type, value=self.info
        ).first()

        if model is None:
            raise ValueError(f"{self.type.name.lower()} does not exists.")

        self.model = model

    def is_valid(self) -> bool:
        if self.type == PeopleDetailTypeChoices.ADDRESS:
            if not validators.phone_number(self.info):
                raise ValueError("invalid phone number.")

        return True

    def add(self, person: People):
        """
        Raises:
            'ValueError': if phone number already exists.
        """

        if PeopleDetailedInfo.objects.filter(
            detail_type=self.type, value=self.info
        ).exists():
            raise ValueError(f"{self.type.name.lower()} already exists.")

        PeopleDetailedInfo.objects.create(
            people=person, detail_type=self.type, value=self.info
        )

    @fetch_model_required
    def change(self, new_info: str) -> None:
        """
        Raises:
            'ValueError': if both values are equal,
            if new value already exists,
            if new value is invalid.
        """

        if self.info == new_info:
            raise ValueError(f"both {self.type.name.lower()} are the same")

        if PeopleDetailedInfo.objects.filter(value=new_info).exists():
            raise ValueError(f"new {self.type.name.lower()} already exists.")

        if not validators.phone_number(new_info):
            raise ValueError(f"invalid {self.type.name.lower()}")

        self.model.value = new_info
        self.model.save()

    @fetch_model_required
    def delete(self):
        """
        Raises:
            'ValueError': if phone number already exists.
        """

        self.model.delete()
