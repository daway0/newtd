from django.db import transaction
from rest_framework.serializers import ValidationError

from . import validators
from .models import People, PeopleDetailedInfo
from .models import PeopleDetailTypeChoices as pdc
from .utils import raise_validation_err


class AddInfo:
    def __init__(
        self, type: pdc.names, info: str, person: People, note: str = None
    ) -> None:
        self.type = type
        self.info = info
        self.person = person
        self.note = note
        self.errors = None

    def is_valid(self) -> bool:
        already_exist = PeopleDetailedInfo.objects.filter(
            value=self.info, detail_type=self.type
        )
        if already_exist.exists():
            self.errors = f"{self.type.name.lower()} already exists."
            return False

        if self.type == pdc.PHONE_NUMBER:

            if not validators.phone_number(self.info):
                self.errors = "invalid phone_number."
                return False

        return True

    def add(self):
        PeopleDetailedInfo.objects.create(
            people=self.person,
            detail_type=self.type,
            value=self.info,
            note=self.note,
        )


class DeleteInfo:
    def __init__(self, info_id: int, type: pdc.names) -> None:
        self.info_id = info_id
        self.type = type
        self.errors = None

    def is_valid(self) -> bool:
        already_exist = PeopleDetailedInfo.objects.filter(pk=self.info_id)
        if not already_exist.exists():
            self.errors = f"{self.type.name.lower()} doesn't exists."
            return False

        return True

    def delete(self):
        info = PeopleDetailedInfo.objects.get(pk=self.info_id)
        info.is_active = False
        info.save()


class EditInfo:
    def __init__(
        self,
        info_id: int,
        type: pdc.names,
        new_info: str = None,
        new_note: str = None,
    ) -> None:
        self.type = type
        self.info = info_id
        self.new_info = new_info
        self.new_note = new_note
        self.errors = None

    def is_valid(self) -> bool:
        self.info = PeopleDetailedInfo.objects.filter(
            pk=self.info, detail_type=self.type
        ).first()
        if self.info is None:
            self.errors = f"invalid {self.type.name.lower()} id."
            return False

        if self.new_note and not self.new_info:
            return True

        if self.type == pdc.PHONE_NUMBER:
            if not validators.phone_number(self.new_info):
                self.errors = "invalid phone_number."
                return False

        if self.info.value == self.new_info:
            self.errors = f"both {self.type.name.lower()}s are the same"
            return False

        if PeopleDetailedInfo.objects.filter(
            value=self.new_info, detail_type=self.type
        ).exists():
            self.errors = f"new {self.type.name.lower()} already exists."
            return False

        return True

    def change(self) -> None:
        if self.new_info is not None:
            self.info.is_active = False

            with transaction.atomic():
                PeopleDetailedInfo.objects.create(
                    detail_type=self.type,
                    people=self.info.people,
                    value=self.new_info,
                    note=self.new_note,
                )
                self.info.save()

            return

        self.info.note = self.new_note
        self.info.save()


class ManipulateInfo:
    def __init__(
        self,
        person: People,
        addresses: list[dict],
        numbers: list[dict],
        card_number: dict,
    ) -> None:
        self.person = person
        self.addresses = addresses
        self.numbers = numbers
        self.card_number = card_number

        self._creation_values = set()
        self._manipulation_values = set()

        self._manipulate_queue: set[dict] = []
        self._creation_queue: set[PeopleDetailedInfo] = []
        self._disable_queue: set[PeopleDetailedInfo] = []

        self._add_addressed_to_creation_queue()
        self._add_numbers_to_creation_queue()
        self._validate_queues()
        self._initiate_manipulation_objs()

    def _add_to_queue(self, data_list, type: pdc.names):
        for data in data_list:
            if data.get("id") is None:
                self._creation_values.add(data["value"])
                self._creation_queue.add(
                    PeopleDetailedInfo(
                        detail_type=type, people=self.person, **data
                    )
                )
            else:
                info = PeopleDetailedInfo.objects.filter(pk=data["id"]).first()
                if info is None:
                    raise_validation_err("DoesNotExists", data["value"])

                self._manipulate_queue.add(
                    {
                        "request_data": data,
                        "info": info,
                    }
                )
                self._manipulation_values.add(data["value"])

    def _validate_queues(self):
        if not self.card_number.get("id"):
            PeopleDetailedInfo.objects.filter(
                detail_type=pdc.CARD_NUMBER, people=self.person
            ).update(is_active=False)

            self._creation_queue.add(
                PeopleDetailedInfo(
                    detail_type=pdc.CARD_NUMBER,
                    people=self.person,
                    **self.card_number,
                )
            )

        else:
            current_card_number = PeopleDetailedInfo.objects.filter(
                id=self.card_number["id"]
            ).first()
            if not current_card_number:
                raise_validation_err(
                    "DoesNotExists", self.card_number["value"]
                )

            if current_card_number.value != self.card_number["value"]:
                self._creation_queue.add(
                    PeopleDetailedInfo(
                        detail_type=pdc.CARD_NUMBER,
                        people=self.person,
                        **self.card_number,
                    )
                )

        duplicates = self._manipulation_values.intersection(
            self._creation_values
        )
        if duplicates:
            raise ValidationError(
                {"code": "DuplicateValues", "values": duplicates}
            )

        duplicates = PeopleDetailedInfo.objects.filter(
            value__in=[*self._creation_values, *self._manipulation_values]
        )
        if duplicates.exists():
            raise ValidationError(
                {
                    "code": "DuplicateValues",
                    "values": duplicates.values_list("value", flat=True),
                }
            )

    def _add_addressed_to_creation_queue(self):
        self._add_to_queue(self.addresses, pdc.ADDRESS)

    def _add_numbers_to_creation_queue(self):
        self._add_to_queue(self.numbers, pdc.PHONE_NUMBER)

    def _initiate_manipulation_objs(self):
        for data in self._manipulate_queue:
            request_data: dict = data["request_data"]
            info: PeopleDetailedInfo = data["info"]

            if request_data["value"] != info.value:
                new_obj = PeopleDetailedInfo(
                    people=self.person,
                    detail_type=info.detail_type,
                    **request_data,
                )
                self._creation_queue.add(new_obj)

                info.is_active = False
                self._disable_queue.add(info)

    def manipulate(self):
        with transaction.atomic():

            PeopleDetailedInfo.objects.bulk_create(self._creation_queue)

            PeopleDetailedInfo.objects.bulk_update(
                self._disable_queue, ["is_active"]
            )
