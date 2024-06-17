from typing import Optional

from rest_framework.serializers import ValidationError

from .models import People, PeopleDetailedInfo
from .models import PeopleDetailTypeChoices as pdc


class ManipulateInfo:
    def __init__(
        self,
        person: People,
        addresses: list[dict],
        numbers: list[dict],
        card_number: Optional[dict],
    ) -> None:
        self.person = person
        self.addresses = addresses
        self.numbers = numbers
        self.card_number = card_number

        self._creation_values = set()
        self._manipulation_values = set()

        self._manipulate_queue: list[dict] = list()
        self._creation_queue: list[PeopleDetailedInfo] = list()
        self._disable_queue: list[PeopleDetailedInfo] = list()
        self._note_manipulations_queue: list[PeopleDetailedInfo] = list()

        if card_number is not None:
            self._add_to_queue(
                [*self.addresses, *self.numbers, self.card_number]
            )
        else:
            self._add_to_queue([*self.addresses, *self.numbers])

        self._validate_queues()
        self._initiate_manipulation_objs()

    def _add_to_queue(self, data_list: pdc.names):
        duplicates = dict()
        presented_ids = set()

        for data in data_list:
            if data.get("id") is None:

                value_len = len(data["value"])
                is_digit = data["value"].isdigit()
                if value_len == 11 and is_digit:
                    type = pdc.PHONE_NUMBER
                elif value_len == 16 and is_digit:
                    type = pdc.CARD_NUMBER
                else:
                    type = pdc.ADDRESS

                self._creation_values.add(data["value"])

                self._creation_queue.append(
                    PeopleDetailedInfo(
                        people=self.person, detail_type=type, **data
                    )
                )
            else:
                duplicates[data["id"]] = data
                presented_ids.add(data["id"])

        infos = PeopleDetailedInfo.actives.filter(pk__in=duplicates.keys())

        for info in infos:
            if duplicates[info.pk]["value"] != info.value:
                self._manipulate_queue.append(
                    {
                        "request_data": duplicates[info.pk],
                        "info": info,
                    }
                )
                self._manipulation_values.add(duplicates[info.pk]["value"])

            elif duplicates[info.pk].get("note") != info.note:

                info.note = duplicates[info.pk].get("note")
                self._note_manipulations_queue.append(info)

        if self.person.pk is None:
            return

        not_presented_infos = PeopleDetailedInfo.actives.exclude(
            pk__in=presented_ids
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

    def _initiate_manipulation_objs(self):
        for data in self._manipulate_queue:
            request_data: dict = data["request_data"]
            info: PeopleDetailedInfo = data["info"]

            if request_data["value"] != info.value:
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
            self._disable_queue, ["is_active"]
        )

        PeopleDetailedInfo.objects.bulk_update(
            self._note_manipulations_queue, ["note"]
        )
