from django.urls import path

from . import views

app_name = "crm"

urlpatterns = [
    # fmt: off
    
    # main sections
    path("dashboard/", views.dashboard_section, name="dashboard_section"),
    path("services/", views.services_section, name="services_section"),
    path("people/", views.people_section, name="people_section"),
    path("payments/", views.payments_section, name="payments_section"),
    path("reports/", views.reports_section, name="reports_section"),
    path("settings/", views.settings_section, name="settings_section"),
    # main sections end

    path("services/<int:id>/", views.get_service, name="get_service"),
    path("orders/<int:id>/", views.get_order, name="get_order"),
    path("contracts/<int:id>/", views.get_contract, name="get_contract"),

    # client related
    path("people/client/create/", views.create_client, name="create_client"),
    path("people/client/<int:id>/", views.edit_client, name="edit_client"),
    path("people/client/<int:id>/update/", views.edit_client, name="update_client"),
    path("people/client/<int:id>/delete/", views.edit_client, name="delete_client"),
    # end client related
     
    path("people/personnel/create/", views.create_personnel, name="create_personnel"),
    path("people/personnel/<int:id>/", views.edit_personnel, name="edit_personnel"),
    path("people/personnel/<int:id>/update/", views.edit_personnel, name="update_personnel"),
    path("people/personnel/<int:id>/delete/", views.delete_personnel, name="delete_personnel"),

    path("people/patient/create/", views.create_patient, name="create_patient"),
    path("people/patient/<int:id>/", views.edit_patient, name="edit_patient"),
    path("people/patient/<int:id>/update/", views.update_patient, name="update_patient"),
    path("people/patient/<int:id>/delete/", views.delete_patient, name="delete_patient"),
    
    # REST
    path("search/", views.search, name="search"),
    path("api/orders/<int:id>/", views.order_preview, name="order_preview"),
    path("api/contracts/<int:id>/", views.contract_preview, name="contract_preview"),
    path("api/clients/<int:id>/", views.client_preview, name="client_preview"),
    path("api/personnel/<int:id>/", views.personnel_preview, name="personnel_preview"),
    path("api/patients/<int:id>/", views.patient_preview, name="patient_preview"),
    # REST end
    # fmt: on
]