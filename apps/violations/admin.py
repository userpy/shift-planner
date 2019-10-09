#
# Copyright 2018 ООО «Верме»
#
# Файл административной панели нарушений
#
from django import forms
from django.contrib.admin import *
from .models import ViolationRule, ViolationRuleItem


class ViolationRuleItemInline(TabularInline):
    model = ViolationRuleItem


@register(ViolationRule)
class ViolationRuleAdmin(ModelAdmin):
    list_display = ('name', 'code', 'icon')
    list_filter = ('pages',)
    search_fields = ('name', 'code')
    inlines = [ViolationRuleItemInline]
