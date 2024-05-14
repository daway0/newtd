from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable

from . import validators
from .models import People, PeopleDetailedInfo


class Info(ABC):
    """
    Abstract class for add/remove/editing people's infos.

    Each info type must have its own set of methods in order to
    correctly do its functionality.
    """

    def __init__(self, info: str) -> None:
        self.info = info
        self.model: PeopleDetailedInfo = None

    @staticmethod
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

    @abstractmethod
    def is_valid(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def fetch_model(self):
        raise NotImplementedError

    @abstractmethod
    def change(self, new_info: str):
        raise NotImplementedError

    @fetch_model_required
    def delete(self):
        self.model.delete()


class PhoneNumber(Info):

    def is_valid(self):
        return validators.phone_number(self.info)

    def fetch_model(self) -> None:
        """
        Raises:
            'ValueError': if info does not exists on db.
        """

        current_obj = PeopleDetailedInfo.objects.filter(
            phone_number=self.info
        ).first()

        if current_obj is None:
            raise ValueError("phone number does not exists.")

        self.model = current_obj

    def add(self, person: People):
        """
        Raises:
            'ValueError': if phone number already exists.
        """

        if PeopleDetailedInfo.objects.filter(phone_number=self.info).exists():
            raise ValueError("phone number already exists.")

        PeopleDetailedInfo.objects.create(
            phone_number=self.info, people=person
        )

    @Info.fetch_model_required
    def change(self, new_info: str) -> None:
        """
        Raises:
            'ValueError': if both phone numbers are equal,
            if new number already exists,
            if new phone number is invalid.
        """

        if self.model.phone_number == new_info:
            raise ValueError("both phone numbers are the same")

        if PeopleDetailedInfo.objects.filter(phone_number=new_info).exists():
            raise ValueError("new phone number already exists.")

        if not validators.phone_number(new_info):
            raise ValueError("invalid new phone number")

        self.model.phone_number = new_info
        self.model.save()
