from . import validators
from .models import People, PeopleDetailedInfo
from .models import PeopleDetailTypeChoices as pdc


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
            self.errors = f"{self.type.name.lower()} doesnt exists."
            return False

        return True

    def delete(self):
        PeopleDetailedInfo.objects.filter(pk=self.info_id).delete()


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
            self.info.value = self.new_info

        if self.new_note is not None:
            self.info.note = self.new_note

        self.info.save()
