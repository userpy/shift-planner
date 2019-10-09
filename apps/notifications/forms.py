from django import forms

from .models import NotifyItem
from apps.lib.forms import JSONFormattedField


class NotifyItemForm(forms.ModelForm):
    class Meta:
        model = NotifyItem
        fields = '__all__'
        field_classes = {
            'params': JSONFormattedField,
        }
        widgets = {
            'params': forms.Textarea(
                attrs={'class': 'acefyelable-textarea', 'data-mode': 'json'}),
        }

    class Media:
        js = ('admin/js/ace/ace.js', 'admin/js/acefy-textarea.js')
