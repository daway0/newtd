from functools import wraps
from typing import Callable

from rest_framework.serializers import ValidationError

from .models import Address, People, PeopleDetailedInfo
from .models import PeopleDetailTypeChoices as pdc


def person_required(func: Callable):
    @wraps(func)
    def wrapper(self, *args, **kwargs):

        if self.person.pk is not None:
            return func(self, *args, **kwargs)

    return wrapper


class ManipulateInfo:
    def __init__(
        self,
        person: People,
        sheba_numbers: list[dict],
        numbers: list[dict],
        card_numbers: list[dict],
    ) -> None:
        self.person = person

        self.sheba_numbers = sheba_numbers
        self.numbers = numbers
        self.card_numbers = card_numbers

        self._creation_values = set()
        self._manipulation_values = set()
        self._presented_infos: dict = dict()

        self._manipulate_queue: list[dict] = list()
        self._creation_queue: list[PeopleDetailedInfo] = list()
        self._disable_queue: list[PeopleDetailedInfo] = list()
        self._note_manipulations_queue: list[PeopleDetailedInfo] = list()

        self._add_to_queue(
            [*self.sheba_numbers, *self.numbers, *self.card_numbers]
        )
        self._find_changed_infos()
        self._notpresented_infos_queue()
        self._validate_queues()
        self._initiate_manipulation_objs()

    def _add_to_queue(self, data_list: dict[str, str]):
        types = {
            16: pdc.CARD_NUMBER,
            24: pdc.SHEBA_NUMBER,
        }

        for data in data_list:
            if data.get("id") is None or self.person.pk is None:

                value_len = len(data["value"])
                # phone numbers doesn't have fixed len.
                type = types.get(value_len, pdc.PHONE_NUMBER)

                self._creation_values.add(data["value"])

                self._creation_queue.append(
                    PeopleDetailedInfo(
                        people=self.person, detail_type=type, **data
                    )
                )
            else:
                self._presented_infos[data["id"]] = data

    @person_required
    def _find_changed_infos(self):
        infos = PeopleDetailedInfo.actives.filter(
            pk__in=self._presented_infos.keys(), people=self.person
        )

        for info in infos:
            if self._presented_infos[info.pk]["value"] != info.value:
                self._manipulate_queue.append(
                    {
                        "request_data": self._presented_infos[info.pk],
                        "info": info,
                    }
                )
                self._manipulation_values.add(
                    self._presented_infos[info.pk]["value"]
                )

            elif self._presented_infos[info.pk].get("note") != info.note:
                info.note = self._presented_infos[info.pk].get("note")
                self._note_manipulations_queue.append(info)

    @person_required
    def _notpresented_infos_queue(self):
        not_presented_infos = PeopleDetailedInfo.actives.exclude(
            pk__in=self._presented_infos.keys()
        ).filter(people=self.person)

        for info in not_presented_infos:
            info.is_active = False
            self._disable_queue.append(info)

    def _validate_queues(self):
        duplicates = self._manipulation_values.intersection(
            self._creation_values
        )
        if duplicates:
            raise ValidationError(
                {
                    "error": [
                        f"مقدار {dup} " "در سیستم وجود دارد و تکراری می‌باشد."
                        for dup in duplicates
                    ],
                }
            )

        duplicates = PeopleDetailedInfo.objects.filter(
            value__in=[*self._creation_values, *self._manipulation_values],
        )
        if duplicates.exists():
            raise ValidationError(
                {
                    "error": [
                        f"مقدار {info.value} "
                        "در سیستم وجود دارد و تکراری می‌باشد."
                        for info in duplicates
                    ],
                }
            )

    @person_required
    def _initiate_manipulation_objs(self):
        for data in self._manipulate_queue:

            request_data: dict = data["request_data"]
            info: PeopleDetailedInfo = data["info"]

            new_obj = PeopleDetailedInfo(
                people=self.person,
                detail_type=info.detail_type,
                value=request_data["value"],
                note=request_data.get("note"),
            )
            self._creation_queue.append(new_obj)

            info.is_active = False
            self._disable_queue.append(info)

    def manipulate(self):

        PeopleDetailedInfo.objects.bulk_create(self._creation_queue)

        PeopleDetailedInfo.objects.bulk_update(
            [*self._disable_queue, *self._note_manipulations_queue],
            ["note", "is_active"],
        )


class ManipulateAddress:
    def __init__(self, person: People, addresses: list[dict]) -> None:
        self.person = person
        self.addresses = addresses

        self._presented_addresses: dict = dict()

        self._create_queue: list[Address] = list()
        self._manipulate_queue: list[dict] = list()
        self._note_manipulations_queue: list[dict] = list()
        self._disable_queue: list[Address] = list()

        self._add_to_queue()
        self._find_changed_addresses()
        self._notpresented_infos_queue()
        self._initiate_manipulated_addresses()

    def _add_to_queue(self):
        for address in self.addresses:
            if address.get("id") is None or self.person.pk is None:
                self._create_queue.append(
                    Address(people=self.person, **address)
                )

            else:
                self._presented_addresses[address["id"]] = address

    @person_required
    def _find_changed_addresses(self):
        addresses = Address.objects.filter(
            pk__in=self._presented_addresses.keys(), people=self.person
        )

        for address in addresses:
            if self._presented_addresses[address.pk]["value"] != address.value:
                self._manipulate_queue.append(
                    {
                        "request_data": self._presented_addresses[address.pk],
                        "address": address,
                    }
                )

            elif (
                self._presented_addresses[address.pk].get("note")
                != address.note
            ):
                address.note = self._presented_addresses[address.pk].get(
                    "note"
                )
                self._note_manipulations_queue.append(address)

    @person_required
    def _notpresented_infos_queue(self):
        not_presented_addresses = Address.objects.exclude(
            pk__in=self._presented_addresses.keys()
        ).filter(people=self.person)

        for address in not_presented_addresses:
            address.is_active = False
            self._disable_queue.append(address)

    def _initiate_manipulated_addresses(self):
        for data in self._manipulate_queue:

            request_data: dict = data["request_data"]
            address: Address = data["address"]

            request_data.pop("id")
            new_obj = Address(
                people=self.person,
                **request_data,
            )
            self._create_queue.append(new_obj)

            address.is_active = False
            self._disable_queue.append(address)

    def save(self):
        if len(self.addresses) == 0:
            return

        Address.objects.bulk_create(self._create_queue)

        Address.objects.bulk_update(
            [*self._disable_queue, *self._note_manipulations_queue],
            ["note", "is_active"],
        )