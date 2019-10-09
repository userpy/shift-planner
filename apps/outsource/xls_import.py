"""
Copyright 2018 ООО «Верме»

Формы загрузки и обработчики XLS документов
"""

from django.http import HttpResponseRedirect
from django import forms
from django.contrib import messages
from django.views.generic import FormView
from django.utils.safestring import mark_safe

from .parsers import OrgLinkXLSParser
from .quotas_xls_parser import QuotasXLSParser
from xlsexport.methods import get_template_by_code


class QuotaImportForm(forms.Form):

    xls_file = forms.FileField()


class QuotasImportView(FormView):

    form_class = QuotaImportForm

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/hq-quotas-list/')

    def post(self, request, *args, **kwargs):

        form = self.get_form()

        if form.is_valid():
            template = get_template_by_code('quota')
            xls = form.cleaned_data['xls_file']
            errors = template.to_import(xls)
            if errors:
                msg = ''.join(['Строка: {} ошибка:{}<br/>'.format(error['rownum'], error['exc'])
                               for error in errors])
                msg = mark_safe(msg)
                messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect('/hq-quotas-list/')

        return HttpResponseRedirect('/hq-quotas-list/')


class QuotasVolumeImportView(FormView):

    form_class = QuotaImportForm

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/hq-quotas-volume-list/')

    def post(self, request, *args, **kwargs):

        form = self.get_form()

        if form.is_valid():
            template = get_template_by_code('quota_volume')
            xls = form.cleaned_data['xls_file']
            errors = template.to_import(xls)
            if errors:
                msg = ''.join(['Строка: {} ошибка:{}<br/>'.format(error['rownum'], error['exc'])
                               for error in errors])
                msg = mark_safe(msg)
                messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect('/hq-quotas-volume-list/')

        return HttpResponseRedirect('/hq-quotas-list/')


class OrgLinkImportForm(forms.Form):
    xls_file = forms.FileField()
