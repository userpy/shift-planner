from .models import RemoteService
from django import forms
from django.contrib import admin


def set_field_html_name(field, new_name):
    """ Create wrapper around the normal widget rendering,
        allowing for a custom field name (new_name).
        http://stackoverflow.com/a/14498608 """
    old_render = field.widget.render

    def _widget_render_wrapper(name, value, attrs=None):
        return old_render(new_name, value, attrs)

    field.widget.render = _widget_render_wrapper


class RemoteServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # костыль для LastPass'а, который в поле пароля на странице редактирования RemoteService'а
        # автоматически вставляет сохранённый пароль от админки, т.е. изменяет поле без спроса
        set_field_html_name(self.fields['password'], 'service_pass')

    def clean_password(self):
        return self.data.get('service_pass')

    class Meta:
        model = RemoteService
        fields = '__all__'


@admin.register(RemoteService)
class RemoteServiceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'code', 'description', 'endpoint', 'protocol', 'is_public', 'method',)
    form = RemoteServiceForm
    fieldsets = (
        ('Основная'.upper(), {
            'fields': ('name', 'description', 'code', 'endpoint', 'action', 'params', 'oneway', 'timeout', 'protocol', 'method'),
        }),
        ('Безопасность'.upper(), {
            'fields': ('login', 'password', 'is_public'),
        }),
    )
