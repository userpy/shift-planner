#
# Copyright 2018 ООО «Верме»
#
# Файл административной панели прав доступа
#

from django import forms
from django.contrib.admin import *
from django.utils.html import format_html
from .models import *


class AccessProfileForm(forms.ModelForm):

    class Meta:
        model = AccessProfile
        fields = '__all__'


class PermissionInline(TabularInline):
    model = Permission
    raw_id_fields = ('role', 'page')
    ordering = ('page_id',)


@register(Page)
class PageAdmin(ModelAdmin):
    list_display = ('name', 'code', 'html_icon',  'party', 'sort_key', 'disabled', 'ext_name', 'parent')
    search_fields = ('name', 'code')
    list_filter = ('party', 'disabled')
    raw_id_fields = ('parent',)
    inlines = [
        PermissionInline
    ]

    def html_icon(self, obj):
        return format_html('<i class="fa fa-{}"></i> ({})', obj.icon, obj.icon)


@register(AccessRole)
class AccessRoleAdmin(ModelAdmin):
    list_display = ('name', 'code', 'party',)
    search_fields = ('name', 'code',)
    list_filter = ('party',)
    inlines = [
        PermissionInline
    ]


@register(AccessProfile)
class AccessProfileAdmin(ModelAdmin):
    list_display = ('headquater', 'role', 'user',  'unit')
    search_fields = ('headquater__name', 'role__name', 'user__username')
    list_filter = ('headquater',)
    fields = ('user', 'role', 'headquater', 'unit_type', 'unit_id')
    raw_id_fields = ('headquater', 'user')
    form = AccessProfileForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.unit:  # добавляем имя орг. единицы как подсказку под полем
            form.base_fields['unit_id'].help_text = obj.unit.name
        return form
