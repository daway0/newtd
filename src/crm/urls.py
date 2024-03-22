from django.urls import path

from . import views

app_name = "crm"

urlpatterns = [
    path("", views.main, name="main"),
    path("people/", views.people_section, name="people_section"),
    path("people/client/", views.new_client, name="new_client"),
    path("people/client/<int:id>", views.edit_client, name="edit_client"),
    path("people/personnel/", views.new_personnel, name="new_personnel"),
    path(
        "people/personnel/<int:id>",
        views.edit_personnel,
        name="edit_personnel",
    ),
    path("people/case/", views.new_case, name="new_case"),
    path("people/case/<int:id>", views.edit_case, name="edit_case"),
]
