from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import models as m


@api_view(["GET"])
def most_requested_services(request):
    report_query = (
        m.OrderServices.objects.select_related("service")
        .values("service", "service__title")
        .annotate(order_numbers=Count("service"))
        .order_by("-order_numbers")[:10]
    )

    return Response(report_query)


def clients_with_most_orders(request):
    report_query = (
        m.People.clients.select_related("client_orders", "client_contracts")
        .annotate(
            client=Concat(
                F("firstname"),
                Value(" "),
                F("lastname"),
            ),
            total_buyouts=Count("client_orders") + Count("client_contracts"),
        )
        .values("client", "total_buyouts")
        .order_by("-total_buyouts")[:10]
    )


def debtor_clients(request):
    report_query = m.DebtorClient.objects.all()[:10]