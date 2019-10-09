#
# Copyright 2018 ООО «Верме»
#
# Файл административной панели претензий
#

from django import forms
from django.contrib.admin import *
from .models import *


@register(ClaimType)
class ClaimTypeAdmin(ModelAdmin):
    list_display = ('name', 'code', 'sort_key')
    search_fields = ('name', 'code')


class ClaimMessageInline(TabularInline):
    model = ClaimMessage


class ClaimAttachInline(TabularInline):
    model = ClaimAttach


class ClaimHistoryInline(TabularInline):
    model = ClaimHistory


class DocumentInline(TabularInline):
    model = Document
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 4, 'cols': 40})},
    }


@register(ClaimRequest)
class ClaimRequestAdmin(ModelAdmin):
    readonly_fields = ('dt_created', 'dt_status_changed', 'number')
    list_display = ('headquater', 'organization', 'agency', 'number', 'status', 'dt_created', 'dt_status_changed')
    search_fields = ('organization__name', 'id', 'text')
    list_filter = ('headquater', 'agency')
    inlines = [
        ClaimMessageInline,
        ClaimAttachInline,
        ClaimHistoryInline
    ]
    fieldsets = (
        ('Основная'.upper(), {
            'fields': (
                'number', 'headquater', 'organization', 'agency', 'claim_type', 'text', 'status', 'dt_created', 'dt_status_changed'
            )
        }),
    )


@register(ClaimStatus)
class ClaimStatusAdmin(ModelAdmin):
    list_display = ('name', 'code', 'sort_key')
    search_fields = ('name', 'code')


@register(ClaimAction)
class ClaimActionAdmin(ModelAdmin):
    list_display = ('name', 'code', 'need_comment', 'sort_key')
    search_fields = ('name', 'code')
