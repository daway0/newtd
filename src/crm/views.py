from django.contrib import messages as msg
from django.db.models import Sum
from django.shortcuts import render

from . import models, utils
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
            utils.summarize_tooman_number(income_past_month),
            "moeny",
            utils.get_diff_in_percentage(
                income_past_month, income_past_2_month
            ),
            summarize_tooman_postfix_word=utils.summarize_tooman_postfix_word(
                income_past_month
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
