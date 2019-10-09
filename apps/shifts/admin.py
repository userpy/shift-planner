#
# Copyright 2018 ООО «Верме»
#
# Файл административной панели заявок и смен
#

from django import forms
from django.contrib.admin import *
from .models import *
from django.db.models import Q
from django.http import HttpResponseRedirect
from xlsexport.methods import get_report_by_code
from xlsexport.mixins import AdminExportMixin
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter


class OutsourcingShiftInline(TabularInline):
    model = OutsourcingShift
    raw_id_fields = ('agency_employee',)


class OutsourcingRequestModelForm(forms.ModelForm):
    class Meta:
        model = OutsourcingRequest
        widgets = {
            'comments': forms.Textarea(attrs={'cols': 80, 'rows': 8}),
            'reject_reason': forms.Textarea(attrs={'cols': 80, 'rows': 8}),
        }
        fields = '__all__'


@register(OutsourcingRequest)
class OutsourcingRequestAdmin(ModelAdmin):
    form = OutsourcingRequestModelForm
    list_display = ('guid', 'agency_name', 'organization_name', 'state', 'dt_accepted', 'dt_ready')
    list_filter = ('state', 'agency')
    inlines = [
        OutsourcingShiftInline,
    ]

    def agency_name(self, obj):
        return obj.agency.name

    agency_name.short_description = 'Агентство'

    def organization_name(self, obj):
        return obj.organization.name

    organization_name.short_description = 'Магазин'

# Пункт Меню Промоутеры/Cмены
@register(PromoShift)
class PromoShiftAdmin(AdminExportMixin, ModelAdmin):
    list_display = (
        'aheadquarter_agency_display',
        'employee_employee_number_display',
        'headquarter',
        'organization',
        'start_end_display',
        'worktime_display',
        'state',
        'dt_change'
    )
    list_filter = (('start', DateRangeFilter), 'state', 'store_area', 'headquarter', 'aheadquarter')
    search_fields = ('agency__name', 'agency__code', 'organization__name', 'organization__code',
                     'agency_employee__firstname', 'agency_employee__surname', 'agency_employee__patronymic',
                     'agency_employee__number', 'start_date', 'guid')
    readonly_fields = ('aheadquarter', 'headquarter', 'dt_change', 'start_date', 'year', 'month', 'day', 'duration')
    raw_id_fields = ('agency', 'organization',)
    actions = ('set_state_delete', 'set_state_accept', 'update_dt_change')
    fieldsets = (
        ('Основная'.upper(), {
            'fields': (
            'state', 'agency', 'organization', 'store_area', 'start', 'end', 'worktime', 'quota_number', 'agency_employee'),
        }),
        ('Системные'.upper(), {
            'fields': ('aheadquarter', 'headquarter', 'dt_change', 'start_date', 'year', 'month', 'day', 'duration'),
        }),
    )

    def set_state_delete(self, request, queryset):
        PromoShift.remove_batch(queryset)
        self.message_user(request, f"Переведено в состояние УДАЛЕНА {queryset.count()} смен")
        return HttpResponseRedirect(request.get_full_path())
    set_state_delete.short_description = "Перевести в состояние УДАЛЕНА"

    def set_state_accept(self, request, queryset):
        PromoShift.restore_batch(queryset)
        self.message_user(request, f"Переведено в состояние ПОДТВЕРЖДЕНА {queryset.count()} смен")
        return HttpResponseRedirect(request.get_full_path())
    set_state_accept.short_description = "Перевести в состояние ПОДТВЕРЖДЕНА"

    def update_dt_change(self, request, queryset):
        queryset.update(dt_change=timezone.now())
        self.message_user(request, f"Метка синхронизации обновлена у {queryset.count()} смен")
        return HttpResponseRedirect(request.get_full_path())
    update_dt_change.short_description = "Обновить метку синхронизации"


@register(Availability)
class Availability(AdminExportMixin, ModelAdmin):
    list_display = (
        'aheadquarter_agency_display',
        'headquarter',
        'organization',
        'start_end_display',
        'dt_change'
    )
    list_filter = ('store_area', 'headquarter', 'aheadquarter')
    search_fields = ('agency__name', 'agency__code', 'organization__name', 'organization__code',
                     'start_date')
    readonly_fields = ('aheadquarter', 'headquarter', 'dt_change')
    raw_id_fields = ('agency', 'organization',)
    fieldsets = (
        ('Основная'.upper(), {
            'fields': (
            'agency', 'organization', 'store_area', 'start', 'end', 'kind'),
        }),
        ('Системные'.upper(), {
            'fields': ('aheadquarter', 'headquarter', 'dt_change'),
        }),
    )
