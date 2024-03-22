from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

# Create your models here.
from . import validators

_WOMAN_PREFIX = "خانم"
_MAN_PREFIX = "آقای"


class Log(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # creator_user = ...
    # last_modifier_user = ...

    class Meta:
        abstract = True


class PeopleTypeChoices(models.TextChoices):
    PERSONNEL = "PSN", "پرسنل"
    CLIENT = "CLI", "کارفرما"
    CASE = "CSE", "مددجو"


class PersonnelRoleChoices(models.TextChoices):
    DOCTOR = "DCTR", "پزشک"
    NURSE = "NRS", "پرستار"
    PRACTICAL_NURSE = "PNRS", "بهیار"
    ASSISTANT_NURSE = "ANRS", "کمک بهیار"
    HOME_CARE = "HCRE", "مراقب"


class GenderChoices(models.TextChoices):
    MALE = "M", "مرد"
    FEMALE = "F", "زن"


class TagSpecefication(models.Model):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.title


class People(Log):
    # general
    national_code = models.CharField(
        max_length=10,
        validators=[
            validators.national_code,
            validators.blacklist_national_codes,
        ],
    )
    firstname = models.CharField(
        max_length=50, validators=[validators.trim_string]
    )
    lastname = models.CharField(
        max_length=50,
        validators=[validators.trim_string],
    )

    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
    )
    birthdate = models.CharField(max_length=10)

    people_type = models.CharField(
        max_length=3,
        choices=PeopleTypeChoices.choices,
    )

    # specific to personnel
    contract_date = models.CharField(max_length=10, null=True)
    end_contract_date = models.CharField(max_length=10, null=True)
    specifications = models.ManyToManyField(TagSpecefication)
    personnel_role = models.CharField(
        max_length=4, choices=PersonnelRoleChoices.choices, null=True
    )

    note = models.TextField(null=True)

    @property
    def full_name(self):
        return f"{self.firstname} {self.lastname}"

    @property
    def fullname_with_prefix(self):
        prefix = (
            _WOMAN_PREFIX
            if self.gender == GenderChoices.FEMALE
            else _MAN_PREFIX
        )
        return f"{prefix} {self.full_name}"

    @property
    def age(self):
        return 52

    @property
    def services_number(self):
        return 12

    @property
    def contracts_number(self):
        return 2

    @property
    def debt_amount(self):
        return 2530000

    def spec_list(self) -> str:
        specs = []
        for spec in self.specifications.all():
            specs.append(spec.title)
        if specs:
            return " ,".join(specs)
        return ""

    def get_absolute_url(self):
        label = None
        for enum in PeopleTypeChoices:
            if enum.value == self.people_type:
                label = enum.name
        path_name = f"crm:edit_{label.lower()}"
        return reverse(path_name, kwargs={"id": self.id})

    def __str__(self) -> str:
        return self.fullname_with_prefix


class PeopleDetailTypeChoices(models.TextChoices):
    ADDRESS = "A", "آدرس"
    PHONE_NUMBER = "P", "شماره تماس"
    CARD_NUMBER = "C", "کارت بانکی"


class PeopleDetailedInfo(models.Model):
    detail_type = models.CharField(
        max_length=1, choices=PeopleDetailTypeChoices.choices
    )

    people = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="details",
    )
    address = models.CharField(max_length=250, null=True)
    phone_number = models.CharField(max_length=10, null=True)
    card_number = models.CharField(max_length=16, null=True)
    note = models.TextField(null=True)

    def __str__(self) -> str:
        detail = self.address or self.phone_number or self.card_number
        return f"{self.detail_type} {detail}"


class Service(models.Model):
    title = models.CharField(max_length=250)
    base_price = models.BigIntegerField()
    healthcare_franchise = models.PositiveSmallIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return f"{self.title}"


class Referral(models.Model):
    title = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.title}"


class Order(Log):
    client = models.ForeignKey(
        People, on_delete=models.CASCADE, related_name="client_orders"
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    assigned_personnel = models.ForeignKey(
        People, on_delete=models.CASCADE, related_name="personnel_orders"
    )
    service_location = models.ForeignKey(
        PeopleDetailedInfo, on_delete=models.CASCADE
    )
    referral_people = models.ForeignKey(
        People, on_delete=models.CASCADE, related_name="referral_orders"
    )
    referral_other = models.ForeignKey(Referral, on_delete=models.CASCADE)
    cost = models.BigIntegerField()
    discount = models.BigIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.client} / {self.assigned_personnel} / {self.service}"


class Contract(Log):
    class CareContractTypeChoices(models.TextChoices):
        ELDER = "E", "سالمند"
        PATIENT = "P", "مددجو"
        KID = "K", "کودک"

    client = models.ForeignKey(
        People, on_delete=models.CASCADE, related_name="client_contracts"
    )
    care_for = models.CharField(
        choices=CareContractTypeChoices.choices, max_length=1
    )
    patients = models.ManyToManyField(People, related_name="patient_contracts")

    class RelationShipChoices(models.TextChoices):
        SELF = "S", "خودشان"
        CHILD = "C", "فرزند"
        PARTNER = "P", "همسر"
        OTHER = "O", "سایر"

    relationship_with_patient = models.CharField(
        choices=RelationShipChoices.choices, max_length=1
    )

    personnel = models.ForeignKey(
        People, on_delete=models.CASCADE, related_name="personnel_contracts"
    )
    service_location = models.ForeignKey(
        PeopleDetailedInfo, on_delete=models.CASCADE
    )

    class ShiftOrderChoices(models.TextChoices):
        DAY = "D", "روزانه"
        NIGHT = "N", "شبانه"
        BOTH = "B", "شبانه روزی"
        OTHER = "O", "سایر"

    shift = models.CharField(choices=ShiftOrderChoices.choices, max_length=1)

    # shifts
    saturday = models.BooleanField(default=True)
    sunday = models.BooleanField(default=True)
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)

    shift_start = models.PositiveSmallIntegerField(default=8)
    shift_end = models.PositiveSmallIntegerField(default=18)

    start = models.CharField(max_length=10)
    end = models.CharField(max_length=10)

    include_holidays = models.BooleanField(default=True)
    personnel_monthly_salary = models.IntegerField(default=0)

    class PaymentTimeChoices(models.TextChoices):
        START = "S", "ابتدای ماه"
        END = "E", "انتهای ماه"
        OTHER = "O", "سایر"

    personnel_salary_payment_time = models.CharField(
        choices=PaymentTimeChoices.choices, max_length=1
    )

    healthcare_franchise_amount = models.IntegerField(default=0)
    referral_people = models.ForeignKey(
        People, on_delete=models.CASCADE, related_name="referral_contracts"
    )
    referral_other = models.ForeignKey(Referral, on_delete=models.CASCADE)


class Payment(Log):

    source = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="source_payments",
        null=True,
    )
    destination = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="dest_payments",
        null=True,
    )
    amount = models.BigIntegerField()
    paid_at = models.CharField(max_length=10)
    note = models.TextField(null=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"from {self.source} to {self.destination} amount {self.amount}"


class Call(models.Model): ...
