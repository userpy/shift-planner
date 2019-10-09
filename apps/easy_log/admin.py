import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import StreamingHttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.http import urlquote
from django.utils.safestring import SafeText
from django.utils.translation import gettext as _

from apps.easy_log.models import LogItem, LogJournal
from apps.easy_log.settings import EASY_LOG, SOURCE
from .paginator import TimeLimitedPaginator
from django.db import connections
from wfm_admin.utils import DateFieldRangeFilter
from apps.easy_log.settings import (ACTION_CHOICES, SOURCE_CHOICES)
from apps.outsource.models import Organization, Agency



def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper

class ChoiceIndexFilter(admin.SimpleListFilter):
    title = ''
    parameter_name = ''
    choices_list = ()

    def lookups(self, request, model_admin):
        def custom_sql():
            query = f"""WITH RECURSIVE t AS (
                    (SELECT {self.parameter_name} FROM easy_log ORDER BY {self.parameter_name} LIMIT 1) UNION ALL
                    SELECT (SELECT {self.parameter_name} FROM easy_log WHERE {self.parameter_name} > t.{self.parameter_name} ORDER BY {self.parameter_name} LIMIT 1)
                    FROM t WHERE t.{self.parameter_name} IS NOT NULL ) SELECT {self.parameter_name} FROM t WHERE {self.parameter_name} IS NOT NULL;"""
            with connections['userlogs'].cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            return rows

        for row in custom_sql():
            for choice in self.choices_list:
                if choice[0] == row[0]:
                    yield(row[0], choice[1])

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        query_dict = dict()
        query_dict.update({f'{self.parameter_name}': self.value()})
        return queryset.filter(Q(**query_dict))


class SourceFilter(ChoiceIndexFilter):
    title = _('Source')
    parameter_name = 'source'
    choices_list = SOURCE_CHOICES


class ActionFilter(ChoiceIndexFilter):
    title = _('action')
    parameter_name = 'action'
    choices_list = ACTION_CHOICES


class LogJournalAdmin(admin.ModelAdmin):

    list_display = ('pk', 'created', 'process_id', 'action', 'status', 'data')
    list_per_page = EASY_LOG.get('ROWS_PER_ACTION')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class LogItemAdmin(admin.ModelAdmin):
    show_full_result_count = False
    paginator = TimeLimitedPaginator

    list_max_show_all = 20
    list_per_page = EASY_LOG.get('ROWS_PER_ACTION')
    list_display = ('pk', 'fdatetime', 'fsource',
                    'action', 'get_headquarter_with_org', 'get_aheadquarter_with_agency', 'get_description')
    readonly_fields = ('pk', 'created', 'process_id',
                       'source', 'source_info', 'action', 'get_username_with_id',
                       'get_headquarter_with_id', 'get_organization_with_id', 'get_aheadquarter_with_id',
                       'get_agency_with_id',
                       'value')
    fields = ('pk', 'created', 'process_id',
              'source', 'source_info', 'action', 'get_username_with_id',
              'get_headquarter_with_id', 'get_organization_with_id', 'get_aheadquarter_with_id',
              'get_agency_with_id',
              'value')
    search_fields = ('process_id', 'source_info', 'id')
    list_filter = (
        ('created', DateFieldRangeFilter),
        ActionFilter,
        SourceFilter,
    )

    def source_combine(self, obj):
        return "{0}<br>{1}".format(obj.get_source_display(), obj.source_info)
    source_combine.short_description = 'Источник'
    source_combine.allow_tags = True

    def fdate(self, obj):
        return timezone.localtime(obj.created).strftime('%d.%m.%Y')
    fdate.short_description = 'Дата'

    def ftime(self, obj):
        return timezone.localtime(obj.created).strftime('%H:%M:%S:%f')[:-3]
    ftime.short_description = 'Время'

    def fdatetime(self, obj):
        return format_html(f'{self.fdate(obj)}<br>{self.ftime(obj)}')
    fdatetime.short_description = 'Дата'
    fdatetime.admin_order_field = 'created'
    fdatetime.allow_tags = True

    def fsource(self, obj):
        if obj.source == SOURCE.EXTERNAL:
            source = 'ScheduleService'
        else:
            source = obj.get_source_display()
        return format_html(f'{self.get_username(obj)}<br>({source})')
    fsource.short_description = _('User')
    fsource.allow_tags = True

    def get_username(self, obj):
        from django.contrib.auth.models import User

        username = '--'
        if obj.user_id:
            user = User.objects.get(pk=obj.user_id)
            username = user.username
        return username

    def get_headquarter(self, obj):
        from apps.outsource.models import Headquater

        headquarter = '--'
        if obj.headquarter:
            headquarter = Headquater.objects.get(pk=obj.headquarter)
            headquarter = headquarter.name
        return headquarter

    def get_headquarter_with_org(self, obj):
        res = self.get_headquarter(obj)
        if obj.organization:
            organization = self.get_organization(obj)
            if organization:
                res += f' ({organization})'
        return res

    get_headquarter_with_org.short_description = 'Клиент'

    def get_aheadquarter(self, obj):
        from apps.outsource.models import Headquater

        aheadquarter = '--'
        if obj.aheadquarter:
            aheadquarter = Headquater.objects.get(pk=obj.aheadquarter)
            aheadquarter = aheadquarter.name
        return aheadquarter

    def get_aheadquarter_with_agency(self, obj):
        res = self.get_aheadquarter(obj)
        if obj.agency:
            agency = self.get_agency(obj)
            if agency:
                res += f' ({agency})'
        return res

    get_aheadquarter_with_agency.short_description = 'Агентство'

    def get_organization(self, obj):
        from apps.outsource.models import Organization

        organization = '--'
        if obj.organization:
            organization = Organization.objects.get(pk=obj.organization)
            organization = organization.name
        return organization

    def get_agency(self, obj):
        from apps.outsource.models import Agency

        agency = '--'
        if obj.agency:
            agency = Agency.objects.get(pk=obj.agency)
            agency = agency.name
        return agency

    def get_username_with_id(self, obj):
        res = self.get_username(obj)
        if obj.user_id:
            res += ' ({pk})'.format(pk=obj.user_id)
        return res
    get_username_with_id.short_description = _('User')

    def get_headquarter_with_id(self, obj):
        res = self.get_headquarter(obj)
        if obj.headquarter:
            res += ' ({pk})'.format(pk=obj.headquarter)
        return res
    get_headquarter_with_id.short_description = 'Клиент'

    def get_organization_with_id(self, obj):
        res = self.get_organization(obj)
        if obj.organization:
            res += ' ({pk})'.format(pk=obj.organization)
        return res
    get_organization_with_id.short_description = 'Орг. единица'

    def get_aheadquarter_with_id(self, obj):
        res = self.get_aheadquarter(obj)
        if obj.aheadquarter:
            res += ' ({pk})'.format(pk=obj.aheadquarter)
        return res
    get_aheadquarter_with_id.short_description = 'Компания агентства'

    def get_agency_with_id(self, obj):
        res = self.get_agency(obj)
        if obj.agency:
            res += ' ({pk})'.format(pk=obj.agency)
        return res
    get_agency_with_id.short_description = 'Агентство'

    def get_description(self, obj, show_full=False):
        from apps.easy_log.presenters import get_presenter_class_factory

        presenter_cls = get_presenter_class_factory(obj.action)
        if not presenter_cls:
            return ''

        presenter = presenter_cls(obj.to_dict())

        desc = presenter.description

        if len(desc) > EASY_LOG['MAX_DESCRIPTION_PREVIEW_LENGTH']:
            new_desc = desc[:EASY_LOG['MAX_DESCRIPTION_PREVIEW_LENGTH'] - 3] + '...'
            desc = SafeText(new_desc) if isinstance(desc, SafeText) else new_desc
        return desc

    get_description.short_description = 'Описание'
    get_description.allow_tags = True

    def get_search_results(self, request, queryset, search_term):
        new_queryset, use_distinct = super(LogItemAdmin, self).get_search_results(
            request, queryset, search_term)

        if not search_term:
            return queryset, use_distinct

        # Ищем по юзеру
        user_ids = list(User.objects.filter(
            Q(username__icontains=search_term) | Q(email__icontains=search_term) |
            Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)
        ).values_list('id', flat=True))
        if user_ids:
            new_queryset |= queryset.filter(user_id__in=user_ids)

        # Ищем по коду магазина
        organization_ids = list(Organization.objects.filter(code=search_term).values_list('id', flat=True))
        if organization_ids:
             new_queryset |= queryset.filter(organization__in=organization_ids)

        # Ищем по коду агентства
        agency_ids = list(Agency.objects.filter(code=search_term).values_list('id', flat=True))
        if agency_ids:
            new_queryset |= queryset.filter(agency__in=agency_ids)


        return new_queryset, use_distinct

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

admin.site.register(LogItem, LogItemAdmin)
admin.site.register(LogJournal, LogJournalAdmin)
