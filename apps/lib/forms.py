import json

from .utils import from_unix
from django import forms
from django.contrib.postgres.forms.jsonb import InvalidJSONInput, JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.models import BaseInlineFormSet
from django.forms.models import ModelChoiceIterator
from itertools import groupby


class UnixDateTimeField(forms.DateTimeField):
    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            value = int(value)
        except ValueError as e:
            raise ValidationError('timestamp is not integer')
        try:
            return from_unix(value)
        except ValueError as e:
            raise ValidationError(e.args[0]) from e


# class SecondsTimeField(forms.DateTimeField):
#     def to_python(self, value):
#         if value in self.empty_values:
#             return None
#         try:
#             value = int(value)
#         except ValueError as e:
#             raise ValidationError('time is not integer')
#         try:
#             return time(value//3600, value//60%60, value%60)
#         except ValueError as e:
#             raise ValidationError(e.args[0]) from e


class IntListField(forms.Field):
    empty_values = [None]

    def to_python(self, value):
        if value is None:
            return None
        try:
            value = json.loads(value)
        except ValueError:
            raise ValidationError('value is not a json list/array')
        if not isinstance(value, list):
            raise ValidationError('value is not a list/array')
        for i in value:
            if not isinstance(i, int):
                raise ValidationError('value is not an int list/array: "%s" is not int' % i)
        return value


class PreparsedIntListField(forms.Field):
    empty_values = [None]

    def to_python(self, value):
        if not isinstance(value, list):
            raise ValidationError('value is not a list/array')
        for i in value:
            if not isinstance(i, int):
                raise ValidationError('value is not an int list/array: "%s" is not int' % i)
        return value


class PreparsedBoolListField(forms.Field):
    empty_values = [None]

    def to_python(self, value):
        if not isinstance(value, list):
            raise ValidationError('value is not a list/array')
        for i in value:
            if not isinstance(i, bool):
                raise ValidationError('value is not a bool list/array: "%s" is not bool' % i)
        return value


class ModelAndIdField(forms.Field):
    def __init__(self, valid_models, lower=False):
        self.model_by_name = dict((m.__name__.lower() if lower else m.__name__, m)
                                  for m in valid_models)
        super().__init__()

    def to_python(self, value):
        if value is None:
            return None
        try:
            model_name, pk_str = value.split('#')
        except ValueError:
            raise ValidationError('wrong value: %s' % value)
        try:
            model = self.model_by_name[model_name]
        except KeyError:
            raise ValidationError('wrong model: %s' % model_name)
        try:
            pk = int(pk_str)
        except ValueError:
            raise ValidationError('wrong id: %s' % pk_str)
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise ValidationError('not found: %s' % value)


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


class GroupedModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, key, *args, **kwargs):
        self.key = key
        super().__init__(*args, **kwargs)

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return GroupedModelChoiceIterator(self, self.key)
    choices = property(_get_choices, forms.ModelMultipleChoiceField._set_choices)


class JSONFormattedField(JSONField):
    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        return json.dumps(value, ensure_ascii=False, indent='  ')


class ColorSelect(forms.widgets.Select):
    BLANK_CHOICE = ('', '---------')
    COLORS = (
        ('Основные', ['#66ade7', '#a8b8d2', '#9cd27c', '#47d9d4', '#d97abb']),
        ('Красные', ['IndianRed', 'LightCoral', 'Salmon', 'DarkSalmon', 'LightSalmon', 'Crimson', 'Red', 'FireBrick', 'DarkRed']),
        ('Розовые', ['Pink', 'LightPink', 'HotPink', 'DeepPink', 'MediumVioletRed', 'PaleVioletRed']),
        ('Оранжевые', ['Coral', 'Tomato', 'OrangeRed', 'DarkOrange', 'Orange']),
        ('Жёлтые', ['Gold', 'Yellow', 'LightYellow', 'LemonChiffon', 'LightGoldenrodYellow',
                    'PapayaWhip', 'Moccasin', 'PeachPuff', 'PaleGoldenrod', 'Khaki', 'DarkKhaki']),
        ('Фиолетовые', ['Lavender', 'Thistle', 'Plum', 'Violet', 'Orchid', 'Fuchsia',
                        'MediumOrchid', 'MediumPurple', 'BlueViolet', 'DarkViolet', 'DarkOrchid',
                        'DarkMagenta', 'Purple', 'Indigo', 'SlateBlue', 'DarkSlateBlue']),
        ('Зелёные', ['GreenYellow', 'Chartreuse', 'LawnGreen', 'Lime', 'LimeGreen', 'PaleGreen',
                     'LightGreen', 'MediumSpringGreen', 'SpringGreen', 'MediumSeaGreen', 'SeaGreen',
                     'ForestGreen', 'Green', 'DarkGreen', 'YellowGreen', 'OliveDrab', 'Olive',
                     'DarkOliveGreen', 'MediumAquamarine', 'DarkSeaGreen', 'LightSeaGreen', 'DarkCyan', 'Teal']),
        ('Синие', ['Aqua', 'LightCyan', 'PaleTurquoise', 'Aquamarine', 'Turquoise', 'MediumTurquoise',
                   'DarkTurquoise', 'CadetBlue', 'SteelBlue', 'LightSteelBlue', 'PowderBlue',
                   'LightBlue', 'SkyBlue', 'LightSkyBlue', 'DeepSkyBlue', 'DodgerBlue', 'CornflowerBlue',
                   'MediumSlateBlue', 'RoyalBlue', 'Blue', 'MediumBlue', 'DarkBlue', 'Navy', 'MidnightBlue']),
        ('Коричневые', ['Cornsilk', 'BlanchedAlmond', 'Bisque', 'NavajoWhite', 'Wheat',
                        'BurlyWood', 'Tan', 'RosyBrown', 'SandyBrown', 'Goldenrod',
                        'DarkGoldenrod', 'Peru', 'Chocolate', 'SaddleBrown', 'Sienna', 'Brown', 'Maroon']),
        ('Белые', ['White', 'Snow', 'Honeydew', 'MintCream', 'Azure', 'AliceBlue',
                   'GhostWhite', 'WhiteSmoke', 'Seashell', 'Beige', 'OldLace',
                   'FloralWhite', 'Ivory', 'AntiqueWhite', 'Linen', 'LavenderBlush', 'MistyRose']),
        ('Серые', ['Gainsboro', 'LightGray', 'Silver', 'DarkGray', 'Gray',
                   'DimGray', 'LightSlateGray', 'SlateGray', 'DarkSlateGray', 'Black']),
    )

    def __init__(self, *args, **kwargs):
        choices = [(group, [(col.lower(), col) for col in colors]) for group, colors in ColorSelect.COLORS]
        kwargs.setdefault('choices', choices)
        super().__init__(*args, **kwargs)

    def optgroups(self, name, value, attrs=None):
        # т.к. self.is_required устанавливается ПОСЛЕ создания, вкостыливаем пустую опцию здесь
        if not self.is_required and (len(self.choices) == 0 or self.choices[0] != self.BLANK_CHOICE):
            self.choices = [self.BLANK_CHOICE] + self.choices
        return super().optgroups(name, value, attrs)

    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)
        option['attrs']['style'] = 'background: ' + option['value']
        return option


class ColorChoiceField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', max(max(len(col) for col in colors) for group, colors in ColorSelect.COLORS))
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorSelect
        return super().formfield(**kwargs)


class AtLeastOneRequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        """ Check that at least one service has been entered """
        super(AtLeastOneRequiredInlineFormSet, self).clean()
        if any(self.errors):
            return
        if not any(not data['DELETE'] for data in self.cleaned_data):
            raise forms.ValidationError('Минимум один элемент должен быть добавлен.')


class PageSelect(forms.widgets.Select):
    BLANK_CHOICE = ('', '---------')
    PAGES = (
        ('Торговые сети', ['claim_frame', 'hq_claim', 'hq_claims_list', 'hq_edit_employee', 'hq_employees_list', 'hq_quotas_list', 'hq_requests_list', 'hq_shifts_confirm', 'hq_shifts_list', 'hq_quotas_volume_list', 'client_schedule']),
        ('Аутсорсинг', ['claim', 'claims_list', 'create_employee', 'edit_employee', 'employees_list', 'requests_list', 'shifts_confirm', 'shifts_list', 'outsource_schedule']),
        ('Промоутеры', ['promo_claim', 'promo_claims_list', 'promo_create_employee', 'promo_edit_employee', 'promo_employees_list', 'promo_schedule']),
        ('Кредитные брокеры', ['broker_claim', 'broker_claims_list', 'broker_create_employee', 'broker_edit_employee', 'broker_employees_list', 'broker_schedule']),
    )

    def __init__(self, *args, **kwargs):
        choices = [(group, [(page.lower(), page) for page in pages]) for group, pages in PageSelect.PAGES]
        kwargs.setdefault('choices', choices)
        super().__init__(*args, **kwargs)

    def optgroups(self, name, value, attrs=None):
        # т.к. self.is_required устанавливается ПОСЛЕ создания, вкостыливаем пустую опцию здесь
        if not self.is_required and (len(self.choices) == 0 or self.choices[0] != self.BLANK_CHOICE):
            self.choices = [self.BLANK_CHOICE] + self.choices
        return super().optgroups(name, value, attrs)

    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)
        return option


class PageChoiceField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', max(max(len(page) for page in pages) for group, pages in PageSelect.PAGES))
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = PageSelect
        return super().formfield(**kwargs)


class ConfigSelect(forms.widgets.Select):
    BLANK_CHOICE = ('', '---------')
    CONFIGS = (
        ('Клиент', [
            ("max_file_size", "Максимальный размер загружаемых файлов, Мб."),
            ("wait_req_template", "Шаблон уведомления - Заявка на аутсорсинг - Новая"),
            ("accept_req_template", "Шаблон уведомления - Заявка на аутсорсинг - Подтверждена"),
            ("reject_req_template", "Шаблон уведомления - Заявка на аутсорсинг - Отклонена"),
            ("delete_shift_template", "Шаблон уведомления - Заявка на аутсорсинг - Отказ от смены"),
            ("create_claim_template", "Шаблон уведомления - Претензия - Новая"),
            ("close_claim_template", "Шаблон уведомления - Претензия - Закрыта"),
            ("accept_claim_template", "Шаблон уведомления - Претензия - Принята"),
            ("reject_claim_template", "Шаблон уведомления - Претензия - Отклонена"),
            ("msg_agency_template", "Шаблон уведомления - Претензия - Сообщение от агентства"),
            ("msg_headquarter_template", "Шаблон уведомления - Претензия - Сообщение от клиента"),
            ("max_shifts_per_day", "Максимальное количество смен сотрудника в день"),
            ("max_files_from_docs", "Максимальное количество документов, запрашиваемых с сервиса хранения образов"),
            ("is_employee_transition", "Разрешено перемещение сотрудников между агенствами")
        ]),
    )

    def __init__(self, *args, **kwargs):
        choices = [(group, [config for config in configs]) for group, configs in ConfigSelect.CONFIGS]
        kwargs.setdefault('choices', choices)
        super().__init__(*args, **kwargs)

    def optgroups(self, name, value, attrs=None):
        # т.к. self.is_required устанавливается ПОСЛЕ создания, вкостыливаем пустую опцию здесь
        # if not self.is_required and (len(self.choices) == 0 or self.choices[0] != self.BLANK_CHOICE):
        self.choices = [self.BLANK_CHOICE] + self.choices
        return super().optgroups(name, value, attrs)

    def create_option(self, *args, **kwargs):
        option = super().create_option(*args, **kwargs)
        return option


class ConfigChoiceField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', max(max(len(config[0]) for config in configs) for group, configs in ConfigSelect.CONFIGS))
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ConfigSelect
        return super().formfield(**kwargs)
