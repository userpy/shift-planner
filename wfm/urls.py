"""
Copyright 2018 ООО «Верме»

Конфигурация url проекта outsourcing
"""

from django.conf.urls import url, include
from django.urls import path
from apps.outsource.views import index, user_login, user_logout, check_user, no_page, no_access,\
    api_get_selector_data, api_get_agency_user_counters, api_check_selected_orgunit,\
    api_quotas_list, hq_quotas_list, api_get_quota_areas_promos, api_quota, api_jobs, api_quotas_volume_list,\
    api_quota_volume, hq_quotas_volume_list, robots_view, ApiAgencyInfoView
from apps.claims.views import claims_list, hq_claims_list, claim, claim_frame, api_get_claims, api_get_claim_messages, \
    api_create_claim, api_create_claim_message, api_create_claim_attachment, api_get_claim_files, api_get_claim,\
    api_get_claim_cities, api_get_claim_stores_agencies_types, api_get_headquater_documents, api_set_claim_action,\
    promo_claims_list, broker_claims_list
from apps.employees.views import create_employee, edit_employee, api_employee, broker_employees_list, \
    employees_list, hq_employees_list, promo_employees_list, api_employees_list, \
    api_get_headquaters_organizations, api_set_employee_recruitment_event, api_dismiss_employee_from_client, api_dismiss_employee,\
    api_org_histories, api_employee_events, api_employee_docs, api_employee_doc, api_doc_types, api_job_histories, api_job_history,\
    api_get_docs_archive, ApiEmployeesListView, ApiTransitionAgencyEmployeeView, ApiAgencyEmployeeHistoryView
from apps.shifts.views import requests_list, hq_requests_list, get_outsourcing_requests, update_request,\
    shifts_list, hq_shifts_list, api_shifts_list, api_shift_employee, shifts_confirm, api_shifts_workload,\
    promo_schedule, api_promo_schedule, api_promo_shift, api_free_employees, hq_shifts_confirm, api_shift_violations,\
    broker_schedule, api_outsource_schedule, outsource_schedule, api_shifts_confirm, client_schedule, api_availability,\
    api_client_schedule, ApiPromoShiftView, ApiClientScheduleView, ApiAvailabilityView, ApiExportEmployeeShiftsView, \
    RedirectPromoShiftGuid


from apps.employees.xls_import import EmployeesImportView
from apps.outsource.xls_import import QuotasImportView, QuotasVolumeImportView
from django.contrib.admin.views.decorators import staff_member_required
from saml.views import admin_login_view

from wfm_admin.admin import wfm_admin

urlpatterns = [
    url(r'^admin/login/$', admin_login_view, name="admin_login"),
    url(r'^admin/', wfm_admin.urls),
    url(r'^$', index),
    url(r'^robots.txt$', robots_view),

    #url(r'^login/$', user_login, name="login_page"),
    url(r'^logout/$', user_logout, name="logout_page"),
    #url(r'^login-check/$', check_user),

    # Заглушки
    url(r'^no-page/$', no_page, name="no_page"),
    url(r'^no-access/$', no_access, name="no_access"),

    # Раздел Аутсорсинг
    url(r'^requests-list/$', requests_list, name="requests_list"),
    url(r'^shifts-list/$', shifts_list, name="shifts_list"),
    url(r'^employees-list/$', employees_list, name="employees_list"),
    url(r'^create-employee/$', create_employee, name="create_employee"),
    url(r'^employee/(?P<employee_id>\d+)$', edit_employee, name="edit_employee"),
    url(r'^claim/$', claim, name="claim"),

    url(r'^update-request/$', update_request, name="update_request"),
    url(r'^shifts-confirm/$', shifts_confirm, name="shifts_confirm"),
    url(r'^claims-list/$', claims_list, name="claims_list"),
    url(r'^outsource-schedule/$', outsource_schedule, name="outsource_schedule"),
    url(r'^api-outsource-schedule/$', api_outsource_schedule, name="api_outsource_schedule"),
    url(r'^api-outsource-shift/$', api_shift_employee, name="api_outsource_shift"),

    # Раздел Клиент
    url(r'^hq-requests-list/$', hq_requests_list, name="hq_requests_list"),
    url(r'^hq-shifts-list/$', hq_shifts_list, name="hq_shifts_list"),
    url(r'^hq-employees-list/$', hq_employees_list, name="hq_employees_list"),
    url(r'^hq-claims-list/$', hq_claims_list, name="hq_claims_list"),
    url(r'^hq-quotas-list/$', hq_quotas_list, name="hq_quotas_list"),
    url(r'^hq-quotas-volume-list/$', hq_quotas_volume_list, name="hq_quotas_volume_list"),

    url(r'^hq-employee/(?P<employee_id>\d+)$', edit_employee, name="hq_edit_employee"),
    url(r'^hq-claim/$', claim, name="hq_claim"),
    url(r'^hq-shifts-confirm/$', hq_shifts_confirm, name="hq_shifts_confirm"),
    url(r'^client-schedule/$', client_schedule, name="client_schedule"),

    # Раздел Промоутер
    url(r'^promo-employees-list/$', promo_employees_list, name="promo_employees_list"),
    url(r'^promo-claims-list/$', promo_claims_list, name="promo_claims_list"),
    url(r'^promo-create-employee/$', create_employee, name="promo_create_employee"),
    url(r'^promo-employee/(?P<employee_id>\d+)$', edit_employee, name="promo_edit_employee"),
    url(r'^promo-claim/$', claim, name="promo_claim"),
    url(r'^promo-schedule/$', promo_schedule, name="promo_schedule"),

    # Раздел Кредитные Брокеры
    url(r'^broker-employees-list/$', broker_employees_list, name="broker_employees_list"),
    url(r'^broker-claims-list/$', broker_claims_list, name="broker_claims_list"),
    url(r'^broker-create-employee/$', create_employee, name="broker_create_employee"),
    url(r'^broker-employee/(?P<employee_id>\d+)$', edit_employee, name="broker_edit_employee"),
    url(r'^broker-claim/$', claim, name="broker_claim"),
    url(r'^broker-schedule/$', broker_schedule, name="broker_schedule"),

    # Методы API
    url(r'^outsourcing-requests/$', get_outsourcing_requests, name="api_requests_list"),

    url(r'^api-shifts-list/$', api_shifts_list, name="api_shifts_list"),
    url(r'^api-shifts-confirm/$', api_shifts_confirm, name="api_shifts_confirm"),
    url(r'^api-shifts-workload/$', api_shifts_workload, name="api_shifts_workload"),
    url(r'^api-shift-employee/$', api_shift_employee, name="api_shift_employee"),
    #url(r'^api-employees-list/$', api_employees_list, name="api_employee_list"),
    url(r'^api-employees-list/$', ApiEmployeesListView.as_view(), name="api_employee_list"),
    url(r'^api-employee/$', api_employee, name="api_employee"),
    url(r'^api-jobs/$', api_jobs, name="api_jobs"),
    url(r'^api-job-histories/$', api_job_histories, name="api_job_histories"),
    url(r'^api-org-histories/$', api_org_histories, name="api_org_histories"),
    url(r'^api-employee-events/$', api_employee_events, name="api_employee_events"),
    url(r'^api-dismiss-employee/$', api_dismiss_employee, name="api_dismiss_employee"),
    url(r'^api-job-history/$', api_job_history, name="api_job_history"),
    url(r'^api-get-headquaters-organizations/$', api_get_headquaters_organizations, name="api_get_headquaters_organizations"),
    url(r'^api-set-employee-recruitment-event/$', api_set_employee_recruitment_event, name="api_set_employee_recruitment_event"),
    url(r'^api-set-employee-dismissal-event/$', api_dismiss_employee_from_client, name="api_dismiss_employee_from_client"),
    url(r'^api-employee-docs/$', api_employee_docs, name="api_employee_docs"),
    url(r'^api-doc-types/$', api_doc_types, name="api_doc_types"),
    url(r'^api-employee-doc/$', api_employee_doc, name="api_employee_doc"),
    url(r'^api-get-docs-archive/$', api_get_docs_archive, name="api_get_docs_archive"),
    url(r'^api-availability/$', ApiAvailabilityView.as_view(), name="api_availability"),
    url(r'^api-transition-agency-employee/$', ApiTransitionAgencyEmployeeView.as_view(), name="api_transition"),
    #url(r'^api-availability/$', api_availability, name="api_availability"),
    url(r'^api-client-schedule/$', api_client_schedule, name="api_client_schedule"),
    url('api-agency-employee-history', ApiAgencyEmployeeHistoryView.as_view(), name='api_agency_employee_history'),
    url('api-export-employee-shifts', ApiExportEmployeeShiftsView.as_view(), name='api_export_employee_shifts'),
    url('api-agency-info', ApiAgencyInfoView.as_view(), name='api_agency_info'),
    # Претензии
    url(r'^api-get-claims/$', api_get_claims, name="api_get_claims"),
    url(r'^api-get-claim/$', api_get_claim, name="api_get_claim"),
    url(r'^api-get-claim-cities/$', api_get_claim_cities, name="api_get_claim_cities"),
    url(r'^api-get-claim-stores-agencies-types/$', api_get_claim_stores_agencies_types, name="api_get_claim_stores_agencies_types"),
    url(r'^api-get-claim-messages/$', api_get_claim_messages, name="api_get_claim_messages"),
    url(r'^api-get-claim-files/$', api_get_claim_files, name="api_get_claim_files"),
    url(r'^api-create-claim/$', api_create_claim, name="api_create_claim"),
    url(r'^api-create-claim-message/$', api_create_claim_message, name="api_create_claim_message"),
    url(r'^api-create-claim-attachment/$', api_create_claim_attachment, name="api_create_claim_attachment"),
    url(r'^api-set-claim-action/$', api_set_claim_action, name="api_set_claim_action"),
    url(r'^api-get-headquater-documents/$', api_get_headquater_documents, name="api_get_headquater_documents"),

    # Промоутеры
    url(r'^api-quotas-list/$', api_quotas_list, name="api_quotas_list"),
    url(r'^api-quota/$', api_quota, name="api_quota"),
    url(r'^api-quotas-volume-list/$', api_quotas_volume_list, name="api_quotas_volume_list"),
    url(r'^api-quota-volume/$', api_quota_volume, name="api_quota_volume"),
    url(r'^api-get-quota-areas-promos/$', api_get_quota_areas_promos, name="api_get_quota_areas_promos"),
    url(r'^api-promo-schedule/$', api_promo_schedule, name="api_promo_schedule"),
    #url(r'^api-client-schedule/$', ApiClientScheduleView.as_view(), name="api_client_schedule"),
    #url(r'^api-promo-shift/$', api_promo_shift, name="api_promo_shift"),
    url(r'^api-promo-shift/$', ApiPromoShiftView.as_view(), name="api_promo_shift"),
    url(r'^api-free-employees/$', api_free_employees, name="api_free_employees"),
    url(r'^api-shift-violations/$', api_shift_violations, name="api_shift_violations"),
                
    # Импорт админка
    url(r'^hq-import-quotas/$', QuotasImportView.as_view(), name='hq_import_quotas'),
    url(r'^hq-import-quotas-volume/$', QuotasVolumeImportView.as_view(), name='hq_import_quotas_volume'),

    # Селекторы
    url(r'^api-get-selector-data/$', api_get_selector_data, name="api_get_selector_data"),
    url(r'^api-check-selected-orgunit/$', api_check_selected_orgunit, name="api_check_selected_orgunit"),

    # Счетчики
    url(r'^api-get-agency-user-counters/$', api_get_agency_user_counters, name="api_get_agency_user_counters"),
    url(r'^testpromo$', RedirectPromoShiftGuid.as_view()),

    # Фреймы
    url(r'^claim-frame/$', claim_frame, name="claim_frame"),

    # Spyne API
    url(r'^api/',       include('apps.api.urls')),

    url(r'^auth/',      include('apps.authutils.urls')),
    url(r'^social/',    include('social_django.urls', namespace='social')),
    url(r'^saml/',      include(('saml.urls', 'saml'), namespace='saml')),

    url(r'^applogs/',   include('applogs.urls')),
    url(r'^xlsexport/', include(('xlsexport.urls', 'xlsexport'), namespace='xlsexport')),

    # Импорт админка
    url(r'^admin/import-employees/$', staff_member_required(EmployeesImportView.as_view()),
        name='admin-employees-import'),
]
