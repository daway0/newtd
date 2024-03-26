from django.urls import path

from . import views

app_name = "crm"

urlpatterns = [
    # main sections
    path("dashboard/", views.dashboard_section, name="dashboard_section"),
    path("services/", views.services_section, name="services_section"),
    path("people/", views.people_section, name="people_section"),
    path("payments/", views.payments_section, name="payments_section"),
    path("reports/", views.reports_section, name="reports_section"),
    path("settings/", views.settings_section, name="settings_section"),
    
    path("people/client/", views.new_client, name="new_client"),
    path("people/client/create", views.new_client, name="new_client"),
    path("people/client/<int:id>/", views.edit_client, name="edit_client"),
    path("people/client/<int:id>/update", views.edit_client, name="edit_client"),
    path("people/client/<int:id>/delete", views.edit_client, name="edit_client"),
    
    path("people/personnel/", views.new_personnel, name="new_personnel"),
    path(
        "people/personnel/<int:id>",
        views.edit_personnel,
        name="edit_personnel",
    ),
    path("people/case/", views.new_case, name="new_case"),
    path("people/case/<int:id>", views.edit_case, name="edit_case"),
    path("search/", views.search, name="search"),
    path("api/orders/<int:id>/", views.order_preview, name="preview"),
]
