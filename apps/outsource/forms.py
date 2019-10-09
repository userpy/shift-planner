"""
Copyright 2018 ООО «Верме»

Формы и поля приложения outsource
"""


from itertools import groupby

from django import forms
from django.forms import ModelForm
from django.forms.models import ModelChoiceIterator

from .models import Agency, Organization, OrgLink


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __init__(self, field, key):
        super().__init__(field)
        self.key = key

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ('', self.field.empty_label)
        queryset = self.queryset.all()
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        groups = groupby(sorted(queryset, key=self.key), self.key)
        for name, objects in groups:
            yield (name, [self.choice(obj) for obj in objects])


class GroupedModelChoiceField(forms.ModelChoiceField):
    def __init__(self, key, *args, **kwargs):
        self.key = key
        super().__init__(*args, **kwargs)

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self, self.key)

    choices = property(_get_choices, forms.ModelChoiceField._set_choices)


class OrgLinkForm(ModelForm):
    class Meta:
        model = OrgLink
        fields = ['headquater', 'organization', 'aheadquarter', 'agency']


class AgencyOrgLinkForm(OrgLinkForm):
    class Meta:
        fields = ['headquater', 'organization']

    def __init__(self, *args, **kwargs):
        super(AgencyOrgLinkForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            headquarter = kwargs['instance'].headquater
            related_organizations = Organization.objects.filter(headquater=headquarter)
            self.fields['organization'] = forms.ModelChoiceField(queryset=related_organizations)


class OrganizationOrgLinkForm(OrgLinkForm):
    class Meta:
        fields = ['aheadquarter', 'agency']

    def __init__(self, *args, **kwargs):
        super(OrganizationOrgLinkForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            aheadquarter = kwargs['instance'].aheadquarter
            related_agencies = Agency.objects.filter(headquater=aheadquarter)
            self.fields['agency'] = forms.ModelChoiceField(queryset=related_agencies)
