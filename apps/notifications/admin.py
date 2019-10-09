# coding=utf-8;

from django.contrib import admin

from .models import NotifyItem
from .forms import NotifyItemForm


class NotifyItemAdmin(admin.ModelAdmin):

    list_display = ('created', 'full_name', 'email', 'send_method', 'template_slug', 'status',)
    fields = ('created', 'full_name', 'email', 'template_slug', 'send_method', 'params', 'status', 'error_text')
    form = NotifyItemForm
    search_fields = ('full_name', 'email', 'template_slug',)
    readonly_fields = ('created',)
    list_filter = ('status', 'send_method','template_slug')


admin.site.register(NotifyItem, NotifyItemAdmin)
