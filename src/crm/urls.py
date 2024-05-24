from django.urls import path

from . import report_views as rv
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
    # previews
    path("search/", views.search, name="search"),
    path("api/orders/<int:id>/", views.order_preview, name="order_preview"),
    path("api/contracts/<int:id>/", views.contract_preview, name="contract_preview"),
    path("api/clients/<int:id>/", views.client_preview, name="client_preview"),
    path("api/personnel/<int:id>/", views.personnel_preview, name="personnel_preview"),
    path("api/patients/<int:id>/", views.patient_preview, name="patient_preview"),
    path("api/services/<int:id>/", views.service_preview, name="service_preview"),
    # previews end

    # Form related
    path("api/forms/personnel/<int:personnel_id>/", views.personnel_form, name="personnel_form"),
    path("api/forms/personnel/", views.personnel_form, name="personnel_form"),
    path("api/forms/clients/<int:client_id>/", views.client_form, name="client_form"),
    path("api/forms/clients/", views.client_form, name="client_form"),
    path("api/forms/patients/<int:patient_id>/", views.patient_form, name="patient_form"),
    path("api/forms/patients/", views.patient_form, name="patient_form"),
    path("api/national-code/<str:national_code>/", views.black_list, name="black_list"),
    path("api/phone-number/", views.edit_phone_number, name="edit_phone_number"),
    path("api/card-number/", views.edit_card_number, name="edit_card_number"),
    path("api/address/", views.edit_address, name="edit_address"),
    # Form related end

    path("api/catalog/", views.catalog, name="catalog"),
    
    # reports
    path("api/reports/most_requested_services/", rv.most_requested_services, name="most_requested_services"),
    path("api/reports/debtor_clients/", rv.debtor_clients, name="debtor_clients"),
    # reports end
    # REST end
    # fmt: on
]
