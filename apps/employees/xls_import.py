from django.http import HttpResponseRedirect
from django import forms
from django.contrib import messages
from django.views.generic import FormView
from django.utils.safestring import mark_safe

from .employees_xls_parser import EmployeesXLSParser


class EmployeeImportForm(forms.Form):

    xls_file = forms.FileField()


class EmployeesImportView(FormView):

    form_class = EmployeeImportForm

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect('/admin/employees/agencyemployee/')

    def post(self, request, *args, **kwargs):

        form = self.get_form()

        if form.is_valid():
            xls = form.cleaned_data['xls_file']
            parser = EmployeesXLSParser()
            errors = parser.parse(file_contents=xls.read())
            if errors:
                msg = ''.join(['Строка: {} ошибка:{}<br/>'.format(error['rownum'], error['exc'])
                               for error in errors])
                msg = mark_safe(msg)
                messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect('/admin/employees/agencyemployee/')

        return HttpResponseRedirect('/admin/employees/agencyemployee/')
