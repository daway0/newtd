from django.contrib import messages as msg
from django.db.models import Q, Sum
from django.shortcuts import render
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
    return render(request, "services/main.html", dict(section="services"))


def people_section(request):
    view_mode = request.GET.get("view_mode")
    qs = models.People.objects.all()
    return render(
        request,
        "people/main.html",
        context=dict(
            section="people",
            people=qs,
            personnel=qs.filter(
                people_type=models.PeopleTypeChoices.PERSONNEL
            ),
            client=qs.filter(people_type=models.PeopleTypeChoices.CLIENT),
            view_mode=view_mode,
        ),
    )


def payments_section(request):
    return render(request, "payments/main.html", dict(section="payments"))


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
    order = models.Order.objects.get(pk=id)
    payment = models.Payment.objects.filter(order=order)

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
                "data": s.PaymentMinimalSerializer(payment, many=True),
            }
        ],
    }
    serializer = s.PreviewSerializer(data).data

    return Response(serializer)
