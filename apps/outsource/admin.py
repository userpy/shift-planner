#
# Copyright 2018 ООО «Верме»
#
# Файл административной панели аутсорсинг
#
from datetime import datetime

from django import forms
from django.contrib.admin import *
from django.db.models import Q
from django.utils import formats, timezone

from apps.claims.admin import DocumentInline
from .models import *
from .methods import *
from .forms import AgencyOrgLinkForm, OrganizationOrgLinkForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from xlsexport.mixins import AdminExportMixin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from rangefilter.filter import DateRangeFilter

def custom_titled_filter(title):
    class Wrapper(FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


# Replaced in OrgLinkAgencyInline by .forms.AgencyOrgLinkForm
class OrgLinkForm(forms.ModelForm):
    def clean(self, *args, **kwargs):
        self.organization = self.cleaned_data['organization']
        self.agency_cleaned = self.cleaned_data['agency']
        super(OrgLinkForm, self).clean(*args, **kwargs)

    def save(self, commit=True):
        orglink = super(OrgLinkForm, self).save(commit=False)
        orglink.headquater = self.organization.headquater
        orglink.save()
        return super(OrgLinkForm, self).save(commit=commit)

    class Meta:
        model = OrgLink
        fields = ['agency', 'organization']


class OrgLinkOrganizationInline(TabularInline):
    model = OrgLink
    form = OrganizationOrgLinkForm
    fields = ('aheadquarter', 'agency')
    readonly_fields = ('aheadquarter',)
    raw_id_fields = ('agency',)
    extra = 0


class OrgLinkAgencyInline(TabularInline):
    model = OrgLink
    form = OrgLinkForm
    fields = ('headquater', 'organization')
    readonly_fields = ('headquater',)
    extra = 0
    raw_id_fields = ('organization', 'headquater')


class ConfigInline(TabularInline):
    model = Config


@register(Headquater)
class HeadquaterAdmin(ModelAdmin):
    list_display = ('name', 'code', 'prefix', 'party')
    search_fields = ('name', 'code')
    list_filter = ('party',)
    inlines = [
        DocumentInline,
        ConfigInline
    ]


class CityListFilter(SimpleListFilter):
    title = 'Город'
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        return [(org.pk, org.name) for org in Organization.objects.filter(~Q(kind='store'))]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(Q(id=self.value()))


class NotNullParentFilter(SimpleListFilter):
    title = 'Агентство'
    parameter_name = 'parent'

    def lookups(self, request, model_admin):
        return (
            ('no', 'Не указано'),
            ('yes', 'Указано'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(parent__isnull=False)

        if self.value() == 'no':
            return queryset.filter(parent__isnull=True)


@register(Organization)
class OrganizationAdmin(ModelAdmin):
    list_display = ('name', 'headquater', 'code', 'kind', 'parent_name', 'address', 'agencies')
    search_fields = ('name', 'code')
    list_filter = ('kind', ('headquater__name', custom_titled_filter('Компания')))
    fields = ('headquater', 'parent', 'name', 'code', 'kind', 'address', 'last_external_update_link',)
    readonly_fields = ('last_external_update_link',)
    inlines = [
        OrgLinkOrganizationInline
    ]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            ids = OrgLink.objects.filter(agency__name__icontains=search_term).values_list('organization_id', flat=True)
            queryset |= self.model.objects.filter(Q(id__in=ids))
        return queryset, use_distinct

    def agencies(self, obj):
        return obj.get_applied_agencies()

    agencies.short_description = 'Агентства'

    def parent_name(self, obj):
        if obj.parent is not None:
            return obj.parent.name
        return None

    parent_name.short_description = 'Вышестоящая орг. единица'

    def last_external_update_link(self, obj):
        if obj.last_external_update is None:
            date_str = 'дата отсутствует'
        else:
            date_str = formats.localize(timezone.template_localtime(obj.last_external_update))
        return date_str

    last_external_update_link.short_description = 'Последнее обновление через API'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Organization.objects.exclude(kind='store')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@register(Agency)
class AgencyAdmin(ModelAdmin):
    list_display = ('name', 'code', 'parent_name', 'job_list', 'headquater')
    search_fields = ('name', 'code')
    fields = ('parent', 'name', 'code', 'jobs', 'headquater',
              'full_name', 'address', 'actual_address', 'phone', 'email', 'site', 'description')
    raw_id_fields = ('headquater', 'parent')
    list_filter = [NotNullParentFilter, 'jobs', ('headquater__name', custom_titled_filter('Компания'))]
    inlines = [
        OrgLinkAgencyInline
    ]

    def job_list(self, obj):
        return ", ".join([j.name for j in obj.jobs.all()])

    job_list.short_description = 'Функции'

    def parent_name(self, obj):
        if obj.parent is not None:
            return obj.parent.name
        return None

    parent_name.short_description = 'Агентство'
    parent_name.admin_order_field = 'name'


@register(StoreArea)
class StoreAreaAdmin(ModelAdmin):
    list_display = ('name', 'code', 'color', 'icon')
    search_fields = ('name', 'code')


@register(QuotaVolume)
class QuotaVolumeAdmin(ModelAdmin):
    list_display = ('store', 'area', 'value', 'start', 'end')
    search_fields = ('area__name', 'area__code', 'store__name', 'store__code')
    raw_id_fields = ('area', 'store')


#Пункт меню промоутеры/Информация по квоте
@register(QuotaInfo)
class QuotaInfoAdmin(ModelAdmin):
    list_display = ('quota', 'month', 'shifts_count', 'open_shifts_count')
    search_fields = ('quota__store__name', 'quota__promo__name')
    raw_id_fields = ('quota', )
    list_filter = (('month', DateRangeFilter),)



#Фильтр для промоутеры/квоты
class QuotaAdminFilter(admin.SimpleListFilter):


    title = 'Магазины'
    parameter_name = 'store_id'

    def lookups(self, request, model_admin):
        headquoter_list = []
        for h in Organization.objects.filter(kind='store'):
            headquoter_list.append((h.id, h.name))
        return headquoter_list


    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(store_id=self.value())
        else:
            return queryset




#Пункт меню промоутеры/квоты
@register(Quota)
class QuotaAdmin(AdminExportMixin, ModelAdmin):
    list_display = ('promo', 'headquarter', 'store', 'quota_type', 'value', 'value_ext')
    fields = ('promo', 'headquarter', 'store', 'area', 'quota_type', 'value', 'value_ext', 'start', 'end')
    search_fields = ('store__name', 'store__code', 'promo__name')
    raw_id_fields = ('headquarter', 'promo', 'store')
    list_filter = (QuotaAdminFilter,)
    actions = ('delete_selected',)

    def delete_selected(self, request, queryset):
        if 'apply' in request.POST:
            remove_quotas(queryset)
            self.message_user(request, f"Удалено {queryset.count()} квот")
            return HttpResponseRedirect(request.get_full_path())
        result_count = 0
        for quota in queryset:
            result_count += get_quota_related_shifts(quota).count()
        return render(request, 'admin/outsource/quota/quota_intermediate.html', context={'quotas': queryset,
                                                                                         'result_count': result_count})
    delete_selected.short_description = "Удалить выбранные квоты"


#Фильтр для OrgLinkAdmin
class OrgLinkOrganizationKindFilter(SimpleListFilter):
    title = 'Тип организации'
    parameter_name = 'organization_kind'

    def lookups(self, request, model_admin):
        return (
            ("store", "Магазин"),
            ("city", "Город"),
            ("head", "Клиент"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(organization__kind=self.value())
        else:
            return queryset

#Пункт меню промоутеры/****
@register(OrgLink)
class OrgLinkAdmin(AdminExportMixin, ModelAdmin):
    list_display = ('headquater', 'organization', 'aheadquarter', 'agency')
    list_filter = (OrgLinkOrganizationKindFilter, 'headquater', 'aheadquarter')
    fields = ('headquater', 'organization', 'aheadquarter', 'agency')
    readonly_fields = ('headquater', 'aheadquarter')

    search_fields = (
        'headquater__name',
        'headquater__code',
        'organization__name',
        'organization__code',
        'aheadquarter__name',
        'aheadquarter__code',
        'agency__name',
        'agency__code',
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'agency':
            # when adding, no object_id in resolver_match
            # otherwise when editing object_id should be present
            if 'object_id' in request.resolver_match.kwargs:
                object_id = request.resolver_match.kwargs['object_id']
                kwargs['queryset'] = OrgLink.objects.get(pk=object_id).aheadquarter.agency_set
        elif db_field.name == 'organization':
            if 'object_id' in request.resolver_match.kwargs:
                object_id = request.resolver_match.kwargs['object_id']
                kwargs['queryset'] = OrgLink.objects.get(pk=object_id).headquater.organization_set
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

