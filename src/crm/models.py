from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q, Sum
from django.db.models.functions import Round
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


class TagSpecefication(Log):
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.title


class ClientManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .filter(people_type=PeopleTypeChoices.CLIENT)
            .order_by("-joined_at")
        )


class PersonnelManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .filter(people_type=PeopleTypeChoices.PERSONNEL)
            .order_by("-joined_at")
        )


class CaseManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .filter(people_type=PeopleTypeChoices.CASE)
            .order_by("-joined_at")
        )


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

    people_type = models.CharField(
        max_length=3,
        choices=PeopleTypeChoices.choices,
    )

    # specific to personnel
    contract_date = models.CharField(max_length=10, null=True, blank=True)
    end_contract_date = models.CharField(max_length=10, null=True, blank=True)
    specifications = models.ManyToManyField(TagSpecefication, blank=True)
    personnel_role = models.CharField(
        max_length=4,
        choices=PersonnelRoleChoices.choices,
        null=True,
        blank=True,
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
    def total_debt(self):
        total_order_costs = (
            self.client_orders.annotate(
                cost=Sum("orderservices__cost"),
            )
            .values("cost", "discount")
            .aggregate(total_cost=Sum("cost") - Sum("discount"))["total_cost"]
            or 0
        )

        total_contract_costs = (
            self.client_contracts.aggregate(
                total_amount=Sum("healthcare_franchise_amount")
            )["total_amount"]
            or 0
        )

        total_paid_amount = (
            self.source_payments.aggregate(total=Sum("amount"))["total"] or 0
        )

        debt = (total_order_costs + total_contract_costs) - total_paid_amount

        return debt if debt >= 0 else 0

    @property
    def total_orders(self):
        return Order.objects.filter(client=self).count()

    @property
    def total_contracts(self):
        return Contract.objects.filter(client=self).count()

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
        return self.fullname_with_prefix

    objects = models.Manager()
    clients = ClientManager()
    personnels = PersonnelManager()
    cases = CaseManager()


class PeopleDetailTypeChoices(models.TextChoices):
    ADDRESS = "A", "آدرس"
    PHONE_NUMBER = "P", "شماره تماس"
    CARD_NUMBER = "C", "کارت بانکی"


class PeopleDetailedInfo(Log):
    detail_type = models.CharField(
        max_length=1, choices=PeopleDetailTypeChoices.choices
    )

    people = models.ForeignKey(
        People,
        on_delete=models.CASCADE,
        related_name="details",
    )
    address = models.CharField(max_length=250, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    card_number = models.CharField(max_length=16, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("crm:get_person_info", kwargs={"id": self.pk})

    def __str__(self) -> str:
        detail = self.address or self.phone_number or self.card_number
        return f"{self.detail_type} {detail}"


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

    def get_absolute_url(self):
        return reverse("crm:get_service", kwargs={"id": self.pk})

    def __str__(self) -> str:
        return f"{self.title}"


class Referral(Log):
    title = models.CharField(max_length=150)

    def get_absolute_url(self):
        return reverse("crm:get_referral", kwargs={"id": self.pk})

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
        franchise = (
            OrderServices.objects.filter(order=self)
            .annotate(
                franchise=Round(
                    F("cost") / 100 * F("service__healthcare_franchise"),
                    3,
                )
            )
            .aggregate(franchise_sum=Sum("franchise"))["franchise_sum"]
        ) or 0

        if self.discount > 0:
            discount_percent = round(
                self.discount / (self.total_cost + self.discount) * 100, 2
            )
            percent_of_franchise = round(franchise / 100 * discount_percent, 2)
            return franchise - percent_of_franchise

        return franchise

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
        cost = OrderServices.objects.filter(order=self).aggregate(
            total_cost=Sum("cost")
        )["total_cost"]
        cost_minus_discount = cost - self.discount

        return cost_minus_discount if cost_minus_discount >= 0 else 0

    @property
    def client_debt(self):
        client_total_payment = Payment.objects.filter(
            source=self.client, order=self
        ).aggregate(total_paid_amount=Sum("amount"))["total_paid_amount"]
        if not client_total_payment:
            return self.total_cost

        return self.total_cost - client_total_payment

    @property
    def debt_to_personnel(self):
        personnel_salary = self.total_cost - self.total_franchise
        paid_salary = Payment.objects.filter(
            destination=self.assigned_personnel
        ).aggregate(total_paid_amount=Sum("amount"))["total_paid_amount"]

        if not paid_salary:
            return personnel_salary

        debt = personnel_salary - paid_salary
        return debt if debt >= 0 else 0

    def get_orders_in_month_ago(month_count: int = 1) -> models.QuerySet:
        start, end = utils.get_month_start_end(month_count)
        return Order.objects.filter(
            Q(order_at__lte=end) & Q(order_at__gte=start)
        )

    def get_absolute_url(self):
        return reverse("crm:get_order", kwargs={"id": self.pk})

    @property
    def services_list(self) -> str:
        return ", ".join(self.services.all().values_list("title", flat=True))

    def __str__(self) -> str:
        return f"{self.client} / {self.assigned_personnel}"


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

    def get_contracts_in_month_ago(month_count: int = 1) -> models.QuerySet:
        start, end = utils.get_month_start_end(month_count)
        return Contract.objects.filter(
            Q(contract_at__lte=end) & Q(contract_at__gte=start)
        )


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

    def get_absolute_url(self):
        return reverse("crm:get_payment", kwargs={"id": self.pk})

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

    def get_all_calls_in_months_ago(month_count: int = 1) -> models.QuerySet:
        start, end = utils.get_month_start_end(month_count)

        return Call.objects.filter(
            Q(called_at__lte=end) & Q(called_at__gte=start)
        )

    def __str__(self) -> str:
        return self.called_at
