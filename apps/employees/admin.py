#
# Copyright 2018 ООО «Верме»
#
# Файл административной панели сотрудников
#

from django import forms
from django.contrib.admin import *
from django.core.exceptions import ValidationError
from .models import *
from .methods import *
from apps.outsource.admin import CityListFilter
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.html import format_html
from urllib.parse import quote_plus
from xlsexport.methods import get_report_by_code

class OrgHistoryForm(forms.ModelForm):

    def clean(self, *args, **kwargs):
        self.organization_cleaned = self.cleaned_data['organization']
        self.agency_employee_cleaned = self.cleaned_data['agency_employee']
        if 'number' not in self.cleaned_data:
            raise ValidationError('Пожалуйста, укажите ТН в организации')
        self.number_cleaned = self.cleaned_data['number']
        if 'start' not in self.cleaned_data:
            raise ValidationError('Пожалуйста, укажите Дату приема')
        self.start_cleaned = self.cleaned_data['start']
        self.end_cleaned = self.cleaned_data['end']
        # Не допускается создание двух разных сотрудников а одном агентстве с одинаковым внешним номером у клиента
        employees = employees_by_ext_number(
            self.organization_cleaned.headquater,
            self.agency_employee_cleaned.agency,
            self.number_cleaned
        )
        if employees.exists() and not self.agency_employee_cleaned in employees:
            raise ValidationError(f'ТН в организации {self.number_cleaned} уже занят сотрудником с ТН {employees.first().number}')
        super(OrgHistoryForm, self).clean(*args, **kwargs)

    def save(self, commit=True):
        orghistory = super(OrgHistoryForm, self).save(commit=False)
        orghistory.headquater = self.organization_cleaned.headquater
        orghistory.save()
        return super(OrgHistoryForm, self).save(commit=commit)

    class Meta:
        model = OrgHistory
        fields = ['organization', 'agency_employee', 'number', 'start', 'end', 'is_inactive']


class JobHistoryInline(TabularInline):
    model = JobHistory


class AgencyHistoryInline(TabularInline):
    model = AgencyHistory
    extra = 0
    raw_id_fields = ('agency_employee',)


class OrgHistoryInline(TabularInline):
    model = OrgHistory
    form = OrgHistoryForm
    extra = 0
    raw_id_fields = ('organization',)


@register(DocType)
class DocTypeAdmin(ModelAdmin):
    list_display = ('name', 'code', 'sort_key')
    search_fields = ('name', 'code')


class EmployeeDocInline(TabularInline):
    model = EmployeeDoc


@register(Job)
class JobAdmin(ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@register(AgencyEmployee)
class AgencyEmployeeAdmin(ModelAdmin):
    list_display = ('name', 'short_number', 'jobs', 'agency_name', 'receipt', 'dismissal')
    search_fields = ('surname', 'firstname', 'patronymic', 'number')
    list_filter = ('agency',)
    readonly_fields = ('last_external_update_link',)
    inlines = [
        JobHistoryInline,
        OrgHistoryInline,
        EmployeeDocInline,
        AgencyHistoryInline,
    ]
    fieldsets = (
        ('Основная'.upper(), {
            'fields': (
                'number', 'firstname', 'surname', 'patronymic',
                'gender', 'date_of_birth', 'place_of_birth', 'agency', 'receipt', 'dismissal',
                'last_external_update_link'
            )
        }),
    )
    actions = ('xls_export', )

    def name(self, object):
        return object.name
    name.short_description = "ФИО"

    def short_number(self, object):
        return object.number
    short_number.short_description = "ТН"

    def agency_name(self, object):
        return object.agency.name
    agency_name.short_description = 'Агентство'

    def last_external_update_link(self, employee):
        if employee.last_external_update is None:
            date_str = 'дата отсутствует'
        else:
            date_str = formats.localize(timezone.template_localtime(employee.last_external_update))
        logs_url = reverse('admin:applogs_serverrecord_changelist') + '?q=employee' + quote_plus('#'+ str(employee.id))
        return format_html('<a href="{}">{}</a>', logs_url, date_str)
    last_external_update_link.short_description = 'Последнее обновление через API'

    def xls_export(self, request, queryset):
        queryset = queryset.select_related('agency').order_by('number')
        #return get_report_by_code('agencyemployee', queryset)
        from datetime import datetime
        from django.http import StreamingHttpResponse
        from django.utils.http import urlquote
        from .xls_export import EmployeesXLSExporter
        #queryset = queryset.select_related('agency').order_by('number')
        response = StreamingHttpResponse(EmployeesXLSExporter().generate(queryset),
                                         content_type='application/vnd.ms-excel')
        today = datetime.now().strftime('%Y%m%d.%H%M%S')
        filename = f'employees.{today}.xls'
        response["Content-Disposition"] = f"attachment; filename*=UTF-8''{urlquote(filename)}"
        return response
    xls_export.short_description = "Выгрузить в Excel"


@register(EmployeeEvent)
class EmployeeEventAdmin(ModelAdmin):
    readonly_fields = ('guid', 'dt_created', 'dt_created_accurate')
    list_display = ('guid', 'agency', 'agency_employee', 'kind', 'organization', 'answer_received', 'dt_created')
    search_fields = ('guid', 'agency_employee__firstname', 'agency_employee__surname', 'agency_employee__patronymic',
                     'agency_employee__number', 'ext_number')
    list_filter = ('kind', 'answer_received', 'agency', CityListFilter, 'headquater',)
    raw_id_fields = ('agency_employee',)

    fieldsets = [
        (None, {'fields': ['guid', 'dt_created_accurate', 'user', 'kind', 'headquater', 'organization', 'agency',
                           'agency_employee', 'answer_received', 'ext_number']}),
        ('Прием', {'fields': ['recruitment_date']}),
        ('Увольнение', {'fields': ['dismissal_date', 'dismissal_reason', 'blacklist']}),
    ]

    def dt_created_accurate(self, object):
        return '{:%Y-%m-%d %H:%M:%S}.{:03d}'.format(object.dt_created, object.dt_created.microsecond // 1000)
    dt_created_accurate.short_description = 'Создано'


@register(EmployeeHistory)
class EmployeeHistoryAdmin(ModelAdmin):
    readonly_fields = ('id', 'dt_created', 'dt_created_accurate')
    list_display = ('id', 'agency', 'agency_employee', 'kind', 'headquater', 'organization')
    search_fields = ('agency_employee__firstname', 'agency_employee__surname', 'agency_employee__patronymic',
                     'agency_employee__number', 'ext_number')
    list_filter = (CityListFilter, 'headquater', 'kind')
    raw_id_fields = ('agency_employee', 'event')

    fieldsets = [
        (None, {'fields': ['id', 'dt_created_accurate', 'user', 'event', 'kind', 'headquater',
                           'organization', 'agency', 'agency_employee', 'ext_number']}),
        ('Прием', {'fields': ['recruitment_date', 'reject_reason']}),
        ('Увольнение', {'fields': ['dismissal_date', 'dismissal_reason', 'blacklist']}),
    ]

    def dt_created_accurate(self, object):
        return '{:%Y-%m-%d %H:%M:%S}.{:03d}'.format(object.dt_created, object.dt_created.microsecond // 1000)
    dt_created_accurate.short_description = 'Создано'


@register(AgencyManager)
class AgencyManagerAdmin(ModelAdmin):
    list_display = ('full_name', 'position', 'phone', 'email')
    search_fields = ('full_name', 'phone', 'email')
    raw_id_fields = ('agency',)
