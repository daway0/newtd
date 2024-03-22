from django.contrib import messages as msg
from django.shortcuts import render

from . import models
from .forms import TestForm


def main(request):
    return render(request, "users/main.html")


def new_client(request):
    form = TestForm()
    return render(
        request, "users/create_change/client.html", context=dict(form=form)
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
        request, "users/create_change/client.html", context=dict(form=form)
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


def people_section(request):
    view_mode = request.GET.get("view_mode")
    qs = models.People.objects.all()
    return render(
        request,
        "users/main.html",
        context=dict(
            people=qs,
            personnel=qs.filter(
                people_type=models.PeopleTypeChoices.PERSONNEL
            ),
            client=qs.filter(people_type=models.PeopleTypeChoices.CLIENT),
            view_mode=view_mode,
        ),
    )
