from typing import Any, Iterable

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q, Sum, Value
from django.db.models.functions import Concat
from django.urls import reverse

from . import utils, validators

_WOMAN_PREFIX = "خانم"
_MAN_PREFIX = "آقای"


class JDateField(models.CharField):
    def __init__(
        self,
        *args: Any,
        max_length=10,
        validators=[validators.jdate_string_validator],
        **kwargs: Any,
    ) -> None:
        super().__init__(
            *args,
            max_length=max_length,
            validators=validators,
            **kwargs,
        )


class Log(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # creator_user = ...
    # last_modifier_user = ...

    class Meta:
        abstract = True


class PeopleTypeChoices(models.TextChoices):
    PERSONNEL = "PERSONNEL", "پرسنل"
    CLIENT = "CLIENT", "کارفرما"
    PATIENT = "PATIENT", "مددجو"


class PersonnelRoleChoices(models.TextChoices):
    DOCTOR = "DOCTOR", "پزشک"
    NURSE = "NURSE", "پرستار"
    PRACTICAL_NURSE = "PRACTICAL_NURSE", "بهیار"
    ASSISTANT_NURSE = "ASSISTANT_NURSE", "کمک بهیار"
    HOME_CARE = "HOME_CARE", "مراقب"


class GenderChoices(models.TextChoices):
    MALE = "M", "مرد"
    FEMALE = "F", "زن"


class Catalog(Log):
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=150)

    # must be in upper case
    code = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.title

    @staticmethod
    def service_location_code() -> str:
        return "LOC"

    @staticmethod
    def tags_code() -> str:
        return "TAG"

    @staticmethod
    def skills_code() -> str:
        return "SKL"

    @staticmethod
    def roles_code() -> str:
        return "ROL"

    @staticmethod
    def types_code() -> str:
        return "TYP"


class ClientManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .prefetch_related("types")
            .filter(types__title="client")
            .order_by("-joined_at")
        )


class PersonnelManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .prefetch_related("types")
            .filter(types__title="personnel")
            .order_by("-joined_at")
        )


class PatientManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .prefetch_related("types")
            .filter(types__title="patient")
            .order_by("-joined_at")
        )


class PeopleCatalogs(models.Model):
    people = models.ForeignKey("People", on_delete=models.CASCADE)
    catalog = models.ForeignKey("Catalog", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.people.fullname_with_prefix} {self.catalog.title}"

    class Meta:
        abstract = True


class Specification(PeopleCatalogs):
    rate = models.IntegerField(null=True, blank=True)


class ServiceLocation(PeopleCatalogs):
    pass


class PeopleRole(PeopleCatalogs):
    pass


class PeopleType(PeopleCatalogs):
    pass


class People(Log):
    joined_at = JDateField()

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

    types = models.ManyToManyField(
        Catalog, related_name="people_types", through=PeopleType
    )

    # specific to personnel
    contract_date = models.CharField(max_length=10, null=True, blank=True)
    end_contract_date = models.CharField(max_length=10, null=True, blank=True)
    specifications = models.ManyToManyField(
        Catalog, related_name="people_specifications", through=Specification
    )
    roles = models.ManyToManyField(
        Catalog, related_name="people_roles", through=PeopleRole
    )
    service_locations = models.ManyToManyField(
        Catalog,
        related_name="people_service_locations",
        through=ServiceLocation,
    )

    note = models.TextField(null=True, blank=True)

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
    def personnel_display_role(self) -> list:
        return self.roles.all().values_list("title", flat=True)

    @property
    def total_personnel_orders(self):
        return self.personnel_orders.count()

    @property
    def total_personnel_contracts(self):
        return self.personnel_contracts.count()

    @property
    def total_healthcare_debt_to_personnel(self):
        debt = OrderPayment.objects.filter(
            order__assigned_personnel=self
        ).aggregate(debt=Sum("personnel_debt"))["debt"]
        return debt if debt and debt >= 0 else 0

    @property
    def total_personnel_additional_payment(self):
        total_revenue_and_paid = OrderPayment.objects.filter(
            order__assigned_personnel=self
        ).aggregate(revenue=Sum("personnel_fee"), paid=Sum("personnel_paid"))

        revenue = total_revenue_and_paid["revenue"]
        paid = total_revenue_and_paid["paid"]
        if not (revenue and paid):
            return 0

        if revenue > paid:
            return 0

        return paid - revenue

    @property
    def total_patient_contracts(self):
        return self.patient_contracts.count()

    @property
    def total_client_debt(self):
        total_order_costs = (
            OrderPayment.objects.filter(order__client=self).aggregate(
                debt=Sum("client_debt")
            )["debt"]
            or 0
        )

        total_contract_costs = (
            self.client_contracts.aggregate(
                total_amount=Sum("healthcare_franchise_amount")
            )["total_amount"]
            or 0
        )

        contract_paid_amount = (
            self.source_payments.filter(order__isnull=True).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        debt = (
            total_order_costs + total_contract_costs
        ) - contract_paid_amount

        return debt if debt >= 0 else 0

    @property
    def total_client_orders(self):
        return Order.objects.filter(client=self).count()

    @property
    def total_client_contracts(self):
        return Contract.objects.filter(client=self).count()

    def get_types(self) -> list[str]:
        return self.types.filter(code=Catalog.roles_code()).values_list(
            "title", flat=True
        )

    def get_roles(self) -> list[str]:
        return self.roles.filter(code=Catalog.types_code()).values_list(
            "title", flat=True
        )

    def spec_list(self) -> str:
        specs = []
        for spec in self.specifications.all():
            specs.append(spec.title)
        if specs:
            return " ,".join(specs)
        return ""

    # def get_absolute_url(self, action_type: str):
    #     assert action_type.lower() in ["create", "edit", "update", "delete"]

    #     label = self.get_types()
    #     path_name = f"crm:{action_type.lower()}_{label.lower()}"

    #     return reverse(path_name, kwargs={"id": self.id})

    def get_absolute_url_api(self):
        types = self.get_types()

        urls = []
        for type in types:
            path = f"crm:{type.lower()}_preview"
            urls.append(reverse(path, kwargs={"id": self.id}))

        return urls

    def get_clients_in_months_ago(month_count: int = 1) -> models.QuerySet:
        start, end = utils.get_month_start_end(month_count)
        return People.clients.filter(
            Q(joined_at__lte=end) & Q(joined_at__gte=start)
        )

    def get_personnel_in_month_ago(month_count: int = 1) -> models.QuerySet:
        start, end = utils.get_month_start_end(month_count)
        return People.personnels.filter(
            Q(joined_at__lte=end) & Q(joined_at__gte=start)
        )

    def __str__(self) -> str:
        types = [type.__str__() for type in self.types.all()]

        return (f"{self.fullname_with_prefix} ({", ".join(types)})")

    objects = models.Manager()
    clients = ClientManager()
    personnels = PersonnelManager()
    patients = PatientManager()


class PeopleDetailTypeChoices(models.TextChoices):
    ADDRESS = "A", "آدرس"
    PHONE_NUMBER = "P", "شماره تماس"
    CARD_NUMBER = "C", "کارت بانکی"


class ActiveInfosManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_active=True)


class PeopleDetailedInfo(Log):
    detail_type = models.CharField(
        max_length=1, choices=PeopleDetailTypeChoices.choices
    )

    people = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="details",
    )
    value = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)
    note = models.TextField(null=True, blank=True)

    objects = models.Manager()
    actives = ActiveInfosManager()

    def __str__(self) -> str:
        return f"{self.people.fullname_with_prefix} {self.detail_type} {self.value}"

    def bulk_phone_numbers(
        phone_numbers: list[dict],
        person: People,
    ):
        return [
            PeopleDetailedInfo(
                detail_type=PeopleDetailTypeChoices.PHONE_NUMBER,
                value=number_obj["number"],
                people=person,
                note=number_obj["note"],
            )
            for number_obj in phone_numbers
        ]


class Service(Log):
    title = models.CharField(max_length=250)
    base_price = models.BigIntegerField()
    healthcare_franchise = models.PositiveSmallIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def healthcare_franchise_in_tooman(self):
        return int(self.base_price / 100 * self.healthcare_franchise)

    @property
    def personnel_franchise(self):
        return 100 - self.healthcare_franchise

    @property
    def personnel_franchise_in_tooman(self):
        return int(self.base_price / 100 * self.personnel_franchise)

    @property
    def total_orders(self):
        return self.order_set.count()

    @property
    def total_orders_in_passed_month(self):
        start, end = utils.get_month_start_end(1)

        return self.order_set.filter(order_at__range=[start, end]).count()

    def get_absolute_url(self):
        return reverse("crm:get_service", kwargs={"id": self.pk})

    def get_absolute_url_api(self):
        return reverse("crm:service_preview", kwargs={"id": self.pk})

    def __str__(self) -> str:
        return f"{self.title}"


class Referral(Log):
    title = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.title}"


class Order(Log):
    order_at = JDateField()
    client = models.ForeignKey(
        People, on_delete=models.CASCADE, related_name="client_orders"
    )
    services = models.ManyToManyField(
        Service, through="OrderServices", symmetrical=False
    )
    assigned_personnel = models.ForeignKey(
        People, on_delete=models.CASCADE, related_name="personnel_orders"
    )
    service_location = models.ForeignKey(
        PeopleDetailedInfo, on_delete=models.CASCADE
    )
    referral_people = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="referral_orders",
        null=True,
        blank=True,
    )
    referral_other = models.ForeignKey(
        Referral, on_delete=models.CASCADE, null=True, blank=True
    )
    discount = models.BigIntegerField(default=0, blank=True)

    @property
    def total_franchise(self):
        return OrderPayment.objects.get(order=self).healthcare_franchise

    @property
    def client_payment_status(self):
        if self.client_debt == 0:
            return "پرداخت شده"
        elif self.client_debt == self.total_cost:
            return "پرداخت نشده"

        return "پرداخت جزئی"

    @property
    def personnel_payment_status(self):
        if self.debt_to_personnel == 0:
            return "پرداخت شده"
        elif self.debt_to_personnel == self.total_cost - self.total_franchise:
            return "پرداخت نشده"

        return "پرداخت جزئی"

    @property
    def total_cost(self):
        return OrderPayment.objects.get(order=self).cost

    @property
    def client_debt(self):
        return OrderPayment.objects.get(order=self).client_debt

    @property
    def debt_to_personnel(self):
        return OrderPayment.objects.get(order=self).personnel_debt

    @property
    def services_list(self) -> str:
        return ", ".join(self.services.all().values_list("title", flat=True))

    def get_orders_in_month_ago(month_count: int = 1) -> models.QuerySet:
        start, end = utils.get_month_start_end(month_count)
        return Order.objects.filter(
            Q(order_at__lte=end) & Q(order_at__gte=start)
        )

    def get_absolute_url_api(self):
        return reverse("crm:order_preview", kwargs={"id": self.pk})

    def __str__(self) -> str:
        return f"خدمت موردی {self.id}"


class OrderServices(Log):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cost = models.PositiveBigIntegerField()


class RelationShipChoices(models.TextChoices):
    SELF = "S", "خودشان"
    CHILD = "C", "فرزند"
    PARTNER = "P", "همسر"
    OTHER = "O", "سایر"


class ShiftOrderChoices(models.TextChoices):
    DAY = "D", "روزانه"
    NIGHT = "N", "شبانه"
    BOTH = "B", "شبانه روزی"
    OTHER = "O", "سایر"


class PaymentTimeChoices(models.TextChoices):
    START = "S", "ابتدای ماه"
    END = "E", "انتهای ماه"
    OTHER = "O", "سایر"


class Contract(Log):
    contract_at = JDateField()

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
    relationship_with_patient = models.CharField(
        choices=RelationShipChoices.choices, max_length=1
    )

    personnel = models.ForeignKey(
        People, on_delete=models.CASCADE, related_name="personnel_contracts"
    )
    service_location = models.ForeignKey(
        PeopleDetailedInfo, on_delete=models.CASCADE
    )

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

    start = JDateField()
    start_hour = models.TimeField()
    end = JDateField()
    end_hour = models.TimeField()

    include_holidays = models.BooleanField(default=True)
    personnel_monthly_salary = models.IntegerField(default=0)

    personnel_salary_payment_time = models.CharField(
        choices=PaymentTimeChoices.choices, max_length=1
    )

    healthcare_franchise_amount = models.IntegerField(default=0)
    referral_people = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="referral_contracts",
        null=True,
        blank=True,
    )
    referral_other = models.ForeignKey(
        Referral, on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def client_debt(self):
        healthcare = People.objects.filter(firstname="مرکز").first()

        total_paid_amount = self.payment_set.filter(
            source=self.client, destination=healthcare
        ).aggregate(total_paid_amount=Sum("amount"))["total_paid_amount"]
        if not total_paid_amount:
            return self.healthcare_franchise_amount

        debt = self.healthcare_franchise_amount - total_paid_amount
        return debt if debt >= 0 else 0

    @property
    def client_payment_status(self):
        if self.client_debt == 0:
            return "پرداخت شده"
        elif self.client_debt == self.healthcare_franchise_amount:
            return "پرداخت نشده"

        return "پرداخت جزئی"

    @property
    def all_patients(self):
        patients = (
            self.patients.all()
            .annotate(
                fullname=Concat(F("firstname"), Value(" "), F("lastname"))
            )
            .values_list("fullname", flat=True)
        )
        return ", ".join(patients) if patients else ""

    def get_contracts_in_month_ago(month_count: int = 1) -> models.QuerySet:
        start, end = utils.get_month_start_end(month_count)
        return Contract.objects.filter(
            Q(contract_at__lte=end) & Q(contract_at__gte=start)
        )

    def get_absolute_url_api(self):
        return reverse("crm:contract_preview", kwargs={"id": self.pk})

    def __str__(self):
        return f"قرارداد {self.id}"


class IncomePaymentManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .filter(destination=None)
            .order_by("-paid_at")
        )


class OutgoPaymentManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(source=None).order_by("-paid_at")


class Payment(Log):
    paid_at = JDateField()
    source = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="source_payments",
        null=True,
        blank=True,
    )
    destination = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="dest_payments",
        null=True,
        blank=True,
    )
    amount = models.BigIntegerField()

    note = models.TextField(null=True, blank=True)

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True, blank=True
    )
    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, null=True, blank=True
    )

    objects = models.Manager()
    incomes = IncomePaymentManager()
    outgoes = OutgoPaymentManager()

    @property
    def payment_for(self):
        return self.order or self.contract

    @property
    def is_income(self):
        return True if self.destination is None else False

    @property
    def is_outgo(self):
        return True if self.source is None else False

    def get_incomes_in_months_ago(month_count: int = 1) -> models.QuerySet:
        start, end = utils.get_month_start_end(month_count)
        return Payment.incomes.filter(
            Q(paid_at__lte=end) & Q(paid_at__gte=start)
        )

    def __str__(self) -> str:
        return f"from {self.source} to {self.destination} amount {self.amount}"


class CallTypeChoices(models.TextChoices):
    RECEIVED = "INC", "ورودی"
    MADE = "OUT", "خروجی"


class StatusChoices(models.TextChoices):
    ANSWERED = "ANS", "پاسخ داده شده"
    NOT_ANSWERED = "REJ", "رد شده"


class Call(Log):
    called_at = JDateField()
    from_people = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="source_calls",
        null=True,
        blank=True,
    )
    from_number = models.CharField(max_length=15, null=True, blank=True)
    to_people = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="dest_calls",
        null=True,
        blank=True,
    )
    to_number = models.CharField(max_length=15, null=True, blank=True)

    duration_in_minutes = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    call_direction = models.CharField(
        max_length=3,
        choices=CallTypeChoices.choices,
    )
    response_status = models.CharField(
        max_length=3,
        choices=StatusChoices.choices,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    note = models.TextField(null=True, blank=True)

    def get_all_calls_in_months_ago(month_count: int = 1) -> models.QuerySet:
        start, end = utils.get_month_start_end(month_count)

        return Call.objects.filter(
            Q(called_at__lte=end) & Q(called_at__gte=start)
        )

    def __str__(self) -> str:
        return self.called_at


class BlackList(models.Model):
    national_code = models.CharField(
        max_length=10,
        validators=[
            validators.national_code,
        ],
        unique=True,
    )

    @staticmethod
    def is_black_listed(national_code: str) -> bool:
        return BlackList.objects.filter(national_code=national_code).exists()


class OrderPayment(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_payment"
    )
    cost_without_discount = models.BigIntegerField()
    cost = models.BigIntegerField()
    healthcare_franchise = models.BigIntegerField()
    personnel_fee = models.BigIntegerField()
    personnel_paid = models.BigIntegerField()
    client_paid = models.BigIntegerField()
    personnel_debt = models.BigIntegerField()
    client_debt = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = "order_payment"


# class DebtorClient(models.Model):
#     client = models.ForeignKey(
#         People, on_delete=models.CASCADE, related_name="debt"
#     )
#     full_name = models.CharField()
#     order_debt = models.PositiveBigIntegerField()
#     contract_debt = models.PositiveBigIntegerField()
#     total_debt = models.PositiveBigIntegerField()

#     class Meta:
#         managed = False
#         db_table = "debtor_client"
