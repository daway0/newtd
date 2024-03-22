from typing import Any, Sequence

from django import forms
from . import models


class StyledCharfiled(forms.CharField):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.widget.attrs["class"] = (
            "p-2 bg-searchbox rounded-md text-black w-full border border-seperatorline"
        )


class StyledChoicefield(forms.ChoiceField):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.widget.attrs["class"] = (
            "p-2 bg-searchbox rounded-md text-black w-full border border-seperatorline"
        )


class TestForm(forms.Form):
    firstname = StyledCharfiled(label="نام")
    lastname = StyledCharfiled(label="نام خانوادگی")
    national_code = StyledCharfiled(label="کد ملی")
    gender = StyledChoicefield(
        choices=models.GenderChoices.choices, label="جنسیت"
    )
    birthdate = StyledCharfiled(label="تاریخ تولد", required=False)
    note = StyledCharfiled(label="یادداشت", required=False)

    def __init__(self, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)

        self.fields["national_code"].widget.attrs["placeholder"] = "0023403616"
        self.fields["firstname"].widget.attrs["placeholder"] = "عرفان"
        self.fields["lastname"].widget.attrs["placeholder"] = "رضایی"
        self.fields["note"].widget.attrs[
            "placeholder"
        ] = "برای یادداشت کردن کلیک کنید..."
