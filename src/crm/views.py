from django.contrib import messages as msg
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models
from . import serializers as s
from . import utils
from .forms import TestForm


def dashboard_section(request):

    # fmt: off
    one_month_ago_client_number = models.People.get_clients_in_months_ago(1).count()
    two_month_ago_client_number = models.People.get_clients_in_months_ago(2).count()

    one_month_ago_calls_number = models.Call.get_all_calls_in_months_ago(1).count()
    two_month_ago_calls_number = models.Call.get_all_calls_in_months_ago(2).count()

    one_month_ago_order_number = models.Order.get_orders_in_month_ago(1).count()
    two_month_ago_order_number = models.Order.get_orders_in_month_ago(2).count()

    one_month_ago_contract_number = models.Contract.get_contracts_in_month_ago(1).count()
    two_month_ago_contract_number = models.Contract.get_contracts_in_month_ago(2).count()

    income_past_month = models.Payment.get_incomes_in_months_ago(1).aggregate(Sum("amount"))["amount__sum"]
    income_past_2_month = models.Payment.get_incomes_in_months_ago(2).aggregate(Sum("amount"))["amount__sum"]
    # fmt: on

    card_stats = [
        utils.make_dashboard_card_data(
            "کارفرمایان جدید",
            one_month_ago_client_number,
            "users",
            utils.get_diff_in_percentage(
                one_month_ago_client_number, two_month_ago_client_number
            ),
        ),
        utils.make_dashboard_card_data(
            "خدمات",
            one_month_ago_order_number,
            "syringe",
            utils.get_diff_in_percentage(
                one_month_ago_order_number, two_month_ago_order_number
            ),
        ),
        utils.make_dashboard_card_data(
            "قرارداد ها",
            one_month_ago_contract_number,
            "users",
            utils.get_diff_in_percentage(
                one_month_ago_contract_number, two_month_ago_contract_number
            ),
        ),
        utils.make_dashboard_card_data(
            "تماس ها ",
            one_month_ago_calls_number,
            "telephone",
            utils.get_diff_in_percentage(
                one_month_ago_calls_number, two_month_ago_calls_number
            ),
        ),
        utils.make_dashboard_card_data(
            "درآمد ناخالص",
            utils.summarize_tooman_number(income_past_month or 0),
            "moeny",
            utils.get_diff_in_percentage(
                income_past_month or 0, income_past_2_month or 0
            ),
            summarize_tooman_postfix_word=utils.summarize_tooman_postfix_word(
                income_past_month or 0
            ),
        ),
    ]

    return render(
        request,
        "dashboard/main.html",
        dict(section="dashboard", static_cards=card_stats),
    )


def services_section(request):
    orders = models.Order.objects.filter().order_by("-order_at")
    contracts = models.Contract.objects.all().order_by("-start")
    services = models.Service.objects.all()
    data = {
        "tabs": [
            utils.make_section_tab(
                "خدمات موردی",
                ["تاریخ", "کارفرما", "کار های انجام شده"],
                orders,
                "services/tables/orders.html",
            ),
            utils.make_section_tab(
                "قراردادها",
                ["تاریخ عقد قرارداد", "کارفرما", "سررسید", "فرانشیز مرکز"],
                contracts,
                "services/tables/contracts.html",
            ),
            utils.make_section_tab(
                "سرویس ها",
                ["عنوان سرویس", "فرانشیز مرکز", "قیمت پیشنهادی پایه"],
                services,
                "services/tables/services.html",
            ),
        ]
    }

    return render(
        request, "services/main.html", dict(section="services", data=data)
    )


def people_section(request):
    clients = models.People.clients.all()
    personnel = models.People.personnels.all()
    cases = models.People.cases.all()
    data = {
        "tabs": [
            utils.make_section_tab(
                "کارفرما",
                [
                    "نام و نام خانوادگی",
                    "خدمات دریافتی",
                    "قرارداد ها",
                    "بدهکاری",
                ],
                clients,
                "people/tables/clients.html",
            ),
            utils.make_section_tab(
                "پرسنل",
                [
                    "نام و نام خانوادگی",
                    "نقش در مرکز",
                    "خدمت دهی",
                    "قرارداد ها",
                    "قابل تسویه",
                ],
                personnel,
                "people/tables/personnel.html",
            ),
            utils.make_section_tab(
                "مددجو",
                ["نام و نام خانوادگی", "قرارداد ها"],
                cases,
                "people/tables/cases.html",
            ),
        ]
    }
    return render(
        request, "people/main.html", dict(section="people", data=data)
    )


def payments_section(request):
    incomes = models.Payment.incomes.all().order_by("-paid_at")
    outgoes = models.Payment.outgoes.all().order_by("-paid_at")
    data = {
        "tabs": [
            utils.make_section_tab(
                "پرداختی کارفرما",
                ["تاریخ واریز", "کارفرما", "بابت", "مبلغ", "یادداشت"],
                incomes,
                "payments/tables/incomes.html",
            ),
            utils.make_section_tab(
                "دریافتی پرسنل",
                ["تاریخ تسویه حساب", "پرسنل", "بابت", "مبلغ", "یادداشت"],
                outgoes,
                "payments/tables/outgoes.html",
            ),
        ]
    }
    return render(
        request, "payments/main.html", dict(section="payments", data=data)
    )


def reports_section(request):
    return render(request, "reports/main.html", dict(section="reports"))


def settings_section(request):
    return render(request, "settings/main.html", dict(section="settings"))


def new_client(request):
    form = TestForm()
    return render(
        request,
        "people/create_change/client.html",
        context=dict(section="people", form=form),
    )


def new_personnel(request):
    form = TestForm()
    return render(
        request, "users/create_change/client.html", context=dict(form=form)
    )


def new_case(request):
    form = TestForm()
    return render(
        request, "users/create_change/client.html", context=dict(form=form)
    )


def edit_client(request, id):
    form = TestForm()
    return render(
        request, "people/create_change/client.html", context=dict(form=form)
    )


def edit_personnel(request, id):
    form = TestForm()
    return render(
        request, "users/create_change/client.html", context=dict(form=form)
    )


def edit_case(request, id):
    form = TestForm()
    return render(
        request, "users/create_change/client.html", context=dict(form=form)
    )


def get_service(request, id):
    service = get_object_or_404(models.Service, pk=id)
    form = TestForm(service)
    return render(request, "some_template", context={"form": form})


def get_person_info(request, id):
    service = get_object_or_404(models.PeopleDetailedInfo, pk=id)
    form = TestForm(service)
    return render(request, "some_template", context={"form": form})


def get_referral(request, id):
    referral = get_object_or_404(models.Referral, pk=id)
    form = TestForm(referral)
    return render(request, "some_template", {"form": form})


def get_order(request, id):
    order = get_object_or_404(models.Order, pk=id)
    form = TestForm(order)
    return render(request, "some_template", {"form": form})


def get_contract(request, id):
    contract = get_object_or_404(models.Contract, pk=id)
    form = TestForm(contract)
    return render(request, "some_template", {"form": form})


def get_payment(request, id):
    payment = get_object_or_404(models.Payment, pk=id)
    form = TestForm(payment)
    return render(request, "some_template", {"form": form})


@api_view(["GET"])
def search(request):
    query: str = request.GET.get("q")
    if not query:
        return Response()

    if query.isdigit():
        people_info = []
        payments = []
        people = []
        if len(query) >= 3:
            people_info = models.PeopleDetailedInfo.objects.filter(
                Q(phone_number__contains=query)
                | Q(card_number__contains=query)
            )
            payments = models.Payment.objects.filter(amount__contains=query)
            people = models.People.objects.filter(
                national_code__contains=query
            )

        if people:
            people.union(
                models.People.objects.filter(
                    Q(birthdate__contains=query)
                    | Q(contract_date__contains=query)
                    | Q(end_contract_date__contains=query)
                )
            )
        else:
            people = models.People.objects.filter(
                Q(birthdate__contains=query)
                | Q(contract_date__contains=query)
                | Q(end_contract_date__contains=query)
            )

        orders = models.Order.objects.filter(
            Q(pk=query) | Q(order_at__contains=query)
        )
        contracts = models.Contract.objects.filter(
            Q(pk=query) | Q(contract_at__contains=query)
        )

        return Response(
            {
                "people_info": s.PeopleDetailsSerializer(
                    people_info, many=True
                ).data,
                "people": s.PeopleSerializer(people, many=True).data,
                "payments": s.PaymentSerializer(payments, many=True).data,
                "orders": s.OrderSerializer(orders, many=True).data,
                "contracts": s.ContractSerializer(contracts, many=True).data,
            }
        )

    if "/" in query:
        people = models.People.objects.filter(birthdate__contains=query)
        orders = models.Order.objects.filter(order_at__contains=query)
        contracts = models.Contract.objects.filter(contract_at__contains=query)

        return Response(
            {
                "people": s.PeopleSerializer(people, many=True).data,
                "orders": s.OrderSerializer(orders, many=True).data,
                "contract": s.ContractSerializer(contracts, many=True).data,
            }
        )

    people = models.People.objects.filter(
        Q(firstname__contains=query) | Q(lastname__contains=query)
    )

    people_info = models.PeopleDetailedInfo.objects.filter(
        address__contains=query
    )

    services = models.Service.objects.filter(title__contains=query)

    tags = models.TagSpecefication.objects.filter(title__contains=query)

    orders = models.Order.objects.filter(
        Q(client__firstname__contains=query)
        | Q(client__lastname__contains=query)
        | Q(assigned_personnel__firstname__contains=query)
        | Q(assigned_personnel__lastname__contains=query)
        | Q(referral_people__firstname__contains=query)
        | Q(referral_people__lastname__contains=query)
        | Q(referral_other__title__contains=query)
    )

    contracts = models.Contract.objects.filter(
        Q(client__firstname__contains=query)
        | Q(client__lastname__contains=query)
        | Q(patients__firstname__contains=query)
        | Q(patients__lastname__contains=query)
        | Q(personnel__firstname__contains=query)
        | Q(personnel__lastname__contains=query)
        | Q(referral_people__firstname__contains=query)
        | Q(referral_people__lastname__contains=query)
        | Q(referral_other__title__contains=query)
    )

    payments = models.Payment.objects.filter(
        Q(source__firstname__contains=query)
        | Q(source__lastname__contains=query)
        | Q(destination__firstname__contains=query)
        | Q(destination__lastname__contains=query)
    )

    json_people = s.PeopleSerializer(people, many=True).data
    json_people_info = s.PeopleDetailsSerializer(people_info, many=True).data
    json_services = s.ServiceSerializer(services, many=True).data
    json_tags = s.SpecificationSerializer(tags, many=True).data
    json_orders = s.OrderSerializer(orders, many=True).data
    json_contracts = s.ContractSerializer(contracts, many=True).data
    json_payments = s.PaymentSerializer(payments, many=True).data

    return Response(
        {
            "people": json_people,
            "people_info": json_people_info,
            "services": json_services,
            "tags": json_tags,
            "orders": json_orders,
            "contracts": json_contracts,
            "payments": json_payments,
        }
    )


@api_view(["GET"])
def order_preview(request, id):
    order = get_object_or_404(models.Order, pk=id)
    payment = models.Payment.objects.filter(order=order)
    data = s.OrderSerializer(order)

    data = {
        "title": "خدمت موردی",
        "icon": "test icon",
        "buttons": [
            {
                "title": "first button",
                "icon": "first button icon",
                "link": "https://test.com/",
            }
        ],
        "table": s.OrderSerializer(order),
        "data_tables": [
            {
                "title": "payment",
                "icon": "payment icon",
                "data": s.PaymentSerializer(
                    payment,
                    fields=["amount", "paid_at", "note", "link"],
                    many=True,
                ),
            }
        ],
    }
    serializer = s.PreviewSerializer(data).data

    return Response(serializer)


@api_view(["GET"])
def contract_preview(request, id):
    contract = get_object_or_404(models.Contract, pk=id)
    payment = models.Payment.objects.filter(contract=contract)

    data = {
        "title": "قرارداد مراقبت",
        "icon": "test icon",
        "buttons": [
            {
                "title": "first button",
                "icon": "first button icon",
                "link": "https://test.com/",
            }
        ],
        "table": s.ContractSerializer(contract),
        "data_tables": [
            {
                "title": "payment",
                "icon": "payment icon",
                "data": s.PaymentSerializer(
                    payment,
                    fields=["amount", "paid_at", "note", "link"],
                    many=True,
                ),
            }
        ],
    }
    serializer = s.PreviewSerializer(data).data

    return Response(serializer)


@api_view(["GET"])
def client_preview(request, id):
    client = get_object_or_404(
        models.People, pk=id, people_type=models.PeopleTypeChoices.CLIENT
    )
    data = {
        "title": "کارفرما",
        "icon": "client icon",
        "buttons": [
            {
                "title": "first button",
                "icon": "first button icon",
                "link": "https://test.com/",
            }
        ],
        "table": s.PeopleSerializer(
            client,
            fields=[
                "total_client_orders",
                "total_clinet_contracts",
                "total_client_debt",
            ],
        ),
        "data_tables": [
            {
                "title": "details",
                "icon": "details icon",
                "data": s.PeopleDetailsSerializer(client.details, many=True),
            },
            {
                "title": "orders",
                "icon": "order icon",
                "data": s.OrderSerializer(
                    client.client_orders.all(),
                    fields=[
                        "order_at",
                        "services",
                        "client_debt",
                        "client_payment_status",
                        "link",
                    ],
                    many=True,
                ),
            },
            {
                "title": "contracts",
                "icon": "contract icon",
                "data": s.ContractSerializer(
                    client.client_contracts.all(),
                    fields=[
                        "start",
                        "start_hour",
                        "end",
                        "end_hour",
                        "end_verbose",
                        "healthcare_franchise_amount",
                        "client_payment_status",
                        "link",
                    ],
                    many=True,
                ),
            },
            {
                "title": "payment",
                "icon": "payment icon",
                "data": s.PaymentSerializer(
                    client.source_payments.all(),
                    fields=["amount", "paid_at", "note", "link"],
                    many=True,
                ),
            },
        ],
    }

    serializer = s.PreviewSerializer(data).data
    return Response(serializer)


@api_view(["GET"])
def personnel_preview(request, id):
    personnel = get_object_or_404(
        models.People, pk=id, people_type=models.PeopleTypeChoices.PERSONNEL
    )

    data = {
        "title": "پرسنل",
        "icon": "personnel icon",
        "buttons": [
            {
                "title": "first button",
                "icon": "first button icon",
                "link": "https://test.com/",
            }
        ],
        "table": s.PeopleSerializer(
            personnel,
            fields=[
                "contract_date",
                "end_contract_date",
                "total_personnel_orders",
                "total_personnel_contracts",
                "total_healthcare_debt_to_personnel",
            ],
        ),
        "data_tables": [
            {
                "title": "details",
                "icon": "details icon",
                "data": s.PeopleDetailsSerializer(
                    personnel.details.all(), many=True
                ),
            },
            {
                "title": "tags",
                "icon": "tags icon",
                "data": s.CommonPatternSerializer(
                    personnel.specifications.all(), many=True
                ),
            },
            {
                "title": "orders",
                "icon": "order icon",
                "data": s.OrderSerializer(
                    personnel.personnel_orders.all(),
                    fields=[
                        "order_at",
                        "services",
                        "debt_to_personnel",
                        "personnel_payment_status",
                        "link",
                    ],
                    many=True,
                ),
            },
            {
                "title": "contracts",
                "icon": "contract icon",
                "data": s.ContractSerializer(
                    personnel.personnel_contracts.all(),
                    fields=[
                        "start",
                        "start_hour",
                        "end",
                        "end_hour",
                        "end_verbose",
                        "healthcare_franchise_amount",
                        "client_payment_status",
                        "link",
                    ],
                    many=True,
                ),
            },
            {
                "title": "payment",
                "icon": "payment icon",
                "data": s.PaymentSerializer(
                    personnel.source_payments.all(),
                    fields=["amount", "paid_at", "note", "link"],
                    many=True,
                ),
            },
        ],
    }

    serializer = s.PreviewSerializer(data).data
    return Response(serializer)


@api_view(["GET"])
def patient_preview(request, id):
    patient = get_object_or_404(
        models.People, pk=id, people_type=models.PeopleTypeChoices.CASE
    )

    data = {
        "title": "بیمار",
        "icon": "patient icon",
        "buttons": [
            {
                "title": "first button",
                "icon": "first button icon",
                "link": "https://test.com/",
            }
        ],
        "table": s.PeopleSerializer(
            patient,
        ),
        "data_tables": [
            {
                "title": "contracts",
                "icon": "contract icon",
                "data": s.ContractSerializer(
                    patient.patient_contracts.all(),
                    fields=[
                        "client",
                        "start",
                        "start_hour",
                        "end",
                        "end_hour",
                        "end_verbose",
                        "link",
                    ],
                    many=True,
                ),
            },
        ],
    }

    serializer = s.PreviewSerializer(data).data
    return Response(serializer)
