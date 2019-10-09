#
# Copyright 2018 ООО «Верме»
#
# Файл моделей
#

from django.db import models
from django.db.models import Q, F
from django.db.models.signals import pre_save, post_delete, post_save, pre_delete
from django.db.utils import ProgrammingError
from django.contrib.auth.models import User
from django.conf import settings
from itertools import chain
from django.utils.safestring import mark_safe
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from apps.lib.forms import ConfigChoiceField
from django.db.models import Sum
import calendar
import datetime
from apps.shifts.signals import *
from .managers import QuotaManager

PARTY_CHOICES = (
    ("client", "Клиент"),
    ("agency", "Аутсорсинг"),
    ("promo", "Вендоры"),
    ("broker", "Кредитный брокер"),
)

ORG_KIND_CHOICES = (  # возможный тип (Organization)
    ("store", "Store"),
    ("city", "City"),
    ("head", "Head"),
)

QUOTA_TYPE_CHOICES = (  # возможный тип (Quota)
    ("fix", "Fix"),
    ("app", "App"),
)

QUOTA_KIND_CHOICES = (  # возможный вид (QuotaValue)
    ("max_by_square", "max_by_square"),
)

CONFIG_KEY_CHOICES = (
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
    ("max_files_from_docs", "Максимальное количество документов, запрашиваемых с сервиса хранения образов")
)

COLORS = (
    ('Основные', ['#66ade7', '#a8b8d2', '#9cd27c', '#47d9d4', '#d97abb']),
    ('Красные',
     ['IndianRed', 'LightCoral', 'Salmon', 'DarkSalmon', 'LightSalmon', 'Crimson', 'Red', 'FireBrick', 'DarkRed']),
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

COLOR_CHOICES = [(group, [(col.lower(), col) for col in colors]) for group, colors in COLORS]


class Headquater(models.Model):
    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Название')
    short = models.CharField(max_length=255, blank=True, null=False, verbose_name='Сокращенное название')
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True,
                            verbose_name='Код')
    prefix = models.CharField(max_length=255, blank=True, verbose_name='Префикс')
    party = models.CharField(max_length=8, choices=PARTY_CHOICES, default=PARTY_CHOICES[0][0],
                             blank=False, null=False, verbose_name="Тип")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Компании"
        verbose_name = "Компания"

    @property
    def has_children(self):
        children = None
        if self.party == 'client':
            children = Organization.objects.filter(headquater_id=self.id).exists()
        elif self.party in ['agency', 'promo', 'broker']:
            children = Agency.objects.filter(headquater_id=self.id).exists()
        if children:
            return True
        return False

    @property
    def full_id(self):
        return f'{self.id}_headquater'

    def __str__(self):
        return self.name


class Organization(models.Model):
    """Организационная структура сети"""
    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Название')
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True,
                            verbose_name='Код')
    kind = models.CharField(max_length=8, choices=ORG_KIND_CHOICES, default=ORG_KIND_CHOICES[0][0],
                            blank=False, null=False, verbose_name="Тип")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT,
                               verbose_name="Вышестоящая орг. единица")
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT,
                                   verbose_name="компания")
    address = models.CharField(max_length=1000, blank=True, verbose_name='Адрес')
    last_external_update = models.DateTimeField(
        verbose_name="Последнее обновление через API", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Клиенты - Орг. структура"
        verbose_name = "Клиенты - Орг. структура"

    def get_unit_with_children(self):
        organizations = set(Organization.objects.filter(id=self.id))
        cur_orgs = set(organizations)
        while len(cur_orgs) > 0:
            cur_orgs = set(Organization.objects.filter(parent_id__in=[o.pk for o in cur_orgs]))
            organizations.update(cur_orgs)
        return organizations

    def get_applied_agencies(self):
        """Список агентств назначенных организации."""
        agency_list = OrgLink.objects.filter(organization=self).values_list('agency__name', flat=True)
        return ', '.join(agency_list)

    def similar_children(self):
        return self.organization_set.order_by('name')

    def children(self):
        return chain(self.organization_set.order_by('name'), self.similar_children())

    @property
    def has_children(self):
        if Organization.objects.filter(parent_id=self.id).exists():
            return True
        return False

    @property
    def full_id(self):
        return f'{self.id}_organization'

    @property
    def full_parent_id(self):
        if self.parent:
            return f'{self.parent_id}_organization'
        return f'{self.headquater_id}_headquater'

    def __str__(self):
        return self.name

    @staticmethod
    def get_children_ids(ids):
        """
        получение всех id детей рекурсивно
        :param ids: list
        :return: list Все id детей
        """
        global_result = []
        while ids:
            ids = Organization.objects.filter(parent_id__in=ids).values_list('id', flat=True).order_by('id')
            global_result += ids
        return global_result


def choices_orgunits(empty=False, exclude=None, start_level=1):
    """
    Создаём набор option для вывода в админке иерархической структуры орг. единиц
    """

    def make_option(unit, option_set, level):
        spaces = ''.join(['&nbsp;'] * 4 * level)
        option = (unit.pk, mark_safe('%s%s' % (spaces, unit.name)))
        if option not in option_set:
            option_set.append(option)
        return option_set

    def dive_deeper(unit, option_set, level):
        option_set = make_option(unit=unit, option_set=option_set, level=level)
        for unit1 in unit.children():
            dive_deeper(unit1, option_set=option_set, level=level + 1)

    option_set = list()
    if empty:
        option_set.append((0, 'Нет'))
    orgs = Organization.objects.filter(parent__isnull=True)
    for org in orgs:
        option_set.append((org.pk, org.name))
        for unit0 in org.children():
            dive_deeper(unit0, option_set, level=start_level)
    return option_set


def choices_orgunits_in_headquaters(empty=False, start_level=1):
    """
    Создаём набор option для вывода в админке иерархической структуры клиентов и их орг. единиц
    """

    def make_option(unit, option_set, level):
        spaces = ''.join(['&nbsp;'] * 4 * level)
        option = (unit.pk, mark_safe('%s%s' % (spaces, unit.name)))
        if option not in option_set:
            option_set.append(option)
        return option_set

    def dive_deeper(unit, option_set, level):
        option_set = make_option(unit=unit, option_set=option_set, level=level)
        for unit1 in unit.children():
            dive_deeper(unit1, option_set=option_set, level=level + 1)

    option_set = list()
    if empty:
        option_set.append((0, 'Нет'))
    # orgs = Organization.objects.filter(parent__isnull=True)
    headquaters = Headquater.objects.all()
    for hq in headquaters:
        hqs_organizations = Organization.objects.filter(headquater=hq, parent__isnull=True)
        hqs_option_set = list()
        for org in hqs_organizations:
            hqs_option_set.append((org.pk, org.name))
            for unit0 in org.children():
                dive_deeper(unit0, hqs_option_set, level=start_level)
        option_set.append((hq.name, hqs_option_set))
    return option_set


class Job(models.Model):
    """Функция, которую может выполнять сотрудник"""
    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Название')
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name='Код')
    color = models.CharField(max_length=120, blank=True, null=True, choices=COLOR_CHOICES,
                             verbose_name='Цвет')
    icon = models.CharField(max_length=120, blank=True, null=True, verbose_name='Иконка')

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Справочник функций"
        verbose_name = "Функция"

    def __str__(self):
        return "{0} / {1}".format(self.name, self.code)


class Agency(models.Model):
    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Название')
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name='Код')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, verbose_name="Агентство")
    jobs = models.ManyToManyField(Job, verbose_name="Функции", blank=True)
    headquater = models.ForeignKey(Headquater, blank=False, null=True, on_delete=models.PROTECT,
                                   verbose_name="компания")
    full_name = models.CharField(max_length=1000, blank=True, null=False, verbose_name='Полное название')
    address = models.CharField(max_length=1000, blank=True, null=False, verbose_name='Юридический адрес')
    actual_address = models.CharField(max_length=1000, blank=True, null=False, verbose_name='Фактический адрес')
    phone = models.CharField(max_length=12, blank=True, null=False, verbose_name='Телефон')
    email = models.EmailField(max_length=100, blank=True, null=False, verbose_name='EMail')
    site = models.CharField(max_length=100, blank=True, null=False, verbose_name='Сайт')
    description = models.TextField(blank=True, null=False, verbose_name='Доп. информация')

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Агентства - Орг. структура"
        verbose_name = "Агентства - Орг. структура"

    @property
    def has_children(self):
        if Agency.objects.filter(parent_id=self.id).exists():
            return True
        return False

    @property
    def full_id(self):
        return f'{self.id}_agency'

    @property
    def full_parent_id(self):
        if self.parent:
            return f'{self.parent_id}_agency'
        return f'{self.headquater_id}_headquater'

    def get_unit_with_children(self):
        organizations = set(Agency.objects.filter(id=self.id))
        cur_orgs = set(organizations)
        while len(cur_orgs) > 0:
            cur_orgs = set(Agency.objects.filter(parent_id__in=[o.pk for o in cur_orgs]))
            organizations.update(cur_orgs)
        return organizations

    def __str__(self):
        return self.name


class OrgLink(models.Model):
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT,
                                   verbose_name="Клиент", related_name='%(app_label)s_headquarters_related',
                                   limit_choices_to={'party': 'client'})
    organization = models.ForeignKey(Organization, blank=False, null=True, on_delete=models.PROTECT,
                                     verbose_name="Организация", related_name='%(app_label)s_organizations_related')

    aheadquarter = models.ForeignKey(Headquater, blank=False, null=True, on_delete=models.PROTECT,
                                     verbose_name="Компания-промоутер",
                                     related_name='%(app_label)s_aheadquarters_related',
                                     limit_choices_to={'party__in': ['agency', 'promo']})
    agency = models.ForeignKey(Agency, blank=False, null=False, on_delete=models.PROTECT, verbose_name="Агентство",
                               related_name='%(app_label)s_agency_related')

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Связи между агентствами и организациями"
        verbose_name = "Связь между агентствами и организациями"

    def __str__(self):
        return "{0} / {1}".format(self.agency, self.organization)


@receiver(pre_save, sender=OrgLink)
def set_org_link_aheadquarter_based_on_agency(sender, instance, **kwargs):
    if not instance.pk:
        instance.aheadquarter = instance.agency.headquater


@receiver(pre_save, sender=OrgLink)
def set_org_link_headquarter_based_on_organization(sender, instance, **kwargs):
    if not instance.pk:
        instance.headquater = instance.organization.headquater


class Config(models.Model):
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Клиент')
    key = ConfigChoiceField(verbose_name='ключ')
    value = models.CharField(max_length=100, verbose_name='Значение', blank=True)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'

    def __str__(self):
        return "{0} / {1}".format(self.headquater, self.key)

    @classmethod
    def get(cls, headquarter, key, default=None):
        try:
            cfg = cls.objects.filter(headquater=headquarter, key=key).first()
        except ProgrammingError:
            return default
        if cfg is None:
            return default
        return cfg.value


class StoreArea(models.Model):
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name='Код')
    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Название')
    color = models.CharField(max_length=120, blank=True, null=True, choices=COLOR_CHOICES,
                             verbose_name='Цвет')
    icon = models.CharField(max_length=120, blank=True, null=True, verbose_name='Иконка')

    class Meta:
        verbose_name = 'Зона магазина '
        verbose_name_plural = 'Зоны магазина'

    def __str__(self):
        return "{0} / {1}".format(self.code, self.name)


class QuotaVolume(models.Model):
    store = models.ForeignKey(Organization, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Магазин')
    area = models.ForeignKey(StoreArea, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Зона магазина')
    value = models.PositiveIntegerField(verbose_name='Значение', default=0)
    kind = models.CharField(max_length=16, choices=QUOTA_KIND_CHOICES, default=QUOTA_KIND_CHOICES[0][0],
                            blank=False, null=False, verbose_name="Вид")
    start = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                             verbose_name="С")
    end = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                           verbose_name="По")

    class Meta:
        verbose_name = 'Объем квот'
        verbose_name_plural = 'Объем квот'

    def __str__(self):
        return "{0} / {1} / {2}".format(self.store, self.area, self.value)

    def get_diff(self, obj):
        if obj is None:
            obj = QuotaVolume()

        if not isinstance(obj, QuotaVolume):
            raise Exception("QuotaVolume.get_diff can apply only QuotaVolume object")

        result = {}
        for attr in ['store', 'area', 'value', 'kind', 'start', 'end']:
            prev_value = getattr(obj, attr)
            new_value = getattr(self, attr)
            if prev_value != new_value:
                if isinstance(prev_value, datetime.date):
                    prev_value = prev_value.isoformat()
                if isinstance(new_value, datetime.date):
                    new_value = new_value.isoformat()
                result.update({
                    attr: {'from': prev_value, 'to': new_value}
                })

        return result


class Quota(models.Model):
    objects = QuotaManager()

    def __str__(self):
        return "{0} / {1} / {2} / {3}".format(self.promo, self.store, self.area, self.quota_type)

    class Meta:
        verbose_name = 'Квота'
        verbose_name_plural = 'Квоты'
        unique_together = ("store", "area", "promo", "start")

    store = models.ForeignKey(Organization, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Магазин')
    area = models.ForeignKey(StoreArea, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Зона магазина')
    promo = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT,
                              limit_choices_to={'party__in': ['promo', 'broker']}, verbose_name='Компания',
                              related_name='%(app_label)s_quotas_promos_related', )
    quota_type = models.CharField(max_length=8, choices=QUOTA_TYPE_CHOICES, default=QUOTA_TYPE_CHOICES[0][0],
                                  blank=False, null=False, verbose_name="Тип")
    value = models.PositiveIntegerField(verbose_name='Стендовые квоты', default=0)
    value_ext = models.PositiveIntegerField(verbose_name='Согласованные квоты', default=0)
    headquarter = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT,
                                    limit_choices_to={'party': 'client'}, verbose_name='Компания клиента',
                                    related_name='%(app_label)s_quotas_headquarters_related', )
    start = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                             verbose_name="С", db_index=True)
    end = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                           verbose_name="По", db_index=True)

    def get_affected_quota_volume(self, month):
        """Получение объема квот на основе переданной квоты и месяца"""
        affected_quota_volume = QuotaVolume.objects.filter(area=self.area, store=self.store)
        if month:
            month_start = datetime.datetime.strptime(month, '%Y-%m-%d').date()
            month_max_day = calendar.monthrange(month_start.year, month_start.month)[1]
            month_end = month_start.replace(day=month_max_day)
            affected_quota_volume = affected_quota_volume. \
                filter(Q(start__lte=month_start, end__gte=month_end) | Q(start__lte=month_start, end__isnull=True))

        if self.end:
            affected_quota_volume = affected_quota_volume. \
                filter(Q(end__gte=self.end) | Q(end__isnull=True))
        else:
            affected_quota_volume = affected_quota_volume. \
                filter(end__isnull=True)
        affected_quota_volume = affected_quota_volume.order_by('-start').first()
        return affected_quota_volume

    def check_if_active(self, month):
        return True if not self.get_similar_area_quotas(month).filter(promo=self.promo, start__gt=self.start).exclude(
            id=self.id).exists() else False

    def get_similar_area_quotas(self, month):
        """Получение списка квот, аналогичных текущей (зона, магазин)"""
        similar_quotas = Quota.objects.filter(area=self.area, store=self.store)
        if month:
            month_start = datetime.datetime.strptime(month, '%Y-%m-%d').date()
            month_max_day = calendar.monthrange(month_start.year, month_start.month)[1]
            month_end = month_start.replace(day=month_max_day)
            similar_quotas = similar_quotas. \
                filter(Q(start__lte=month_start, end__gte=month_end) | Q(start__lte=month_start, end__isnull=True))

        similar_quotas = similar_quotas.order_by('promo_id', '-start').distinct('promo_id').values_list('id', flat=True)
        return Quota.objects.filter(id__in=similar_quotas)

    def get_diff(self, obj):
        if obj is None:
            obj = Quota()

        if not isinstance(obj, Quota):
            raise Exception("Quota.get_diff can apply only Quota object")

        result = {}
        changed_attrs = list()
        for attr in ['store', 'area', 'promo', 'quota_type', 'value', 'value_ext', 'start', 'end']:
            prev_value = getattr(obj, attr)
            new_value = getattr(self, attr)
            if prev_value != new_value:
                if isinstance(prev_value, datetime.date):
                    prev_value = prev_value.isoformat()
                if isinstance(new_value, datetime.date):
                    new_value = new_value.isoformat()
                changed_attrs.append(attr)
                result.update({
                    attr: {'from': prev_value, 'to': new_value}
                })
        from apps.outsource.methods import get_quota_related_shifts
        prev_object_related_shifts = get_quota_related_shifts(obj)
        if 'start' in changed_attrs and 'end' not in changed_attrs:
            # Сдвинули начало влево (увеличили интервал), ищем смены больше start
            if getattr(self, 'start') < getattr(obj, 'start'):
                pending_shifts = prev_object_related_shifts.filter(start__gte=self.start,
                                                                   start__lt=obj.start)
            # вправо (уменьшили интервал), ищем меньше start
            else:
                pending_shifts = prev_object_related_shifts.filter(start__lt=self.start,
                                                                   start__gte=obj.start)
        if 'start' not in changed_attrs and 'end' in changed_attrs:
            # Сдвинули конец влево (уменьшили интервал), ищем смены больше end
            if getattr(self, 'end') < getattr(obj, 'end'):
                pending_shifts = prev_object_related_shifts.filter(end__gt=self.end,
                                                                   end__lte=obj.end)
            # вправо (увеличили интервал), ищем меньше end
            else:
                pending_shifts = prev_object_related_shifts.filter(end__gt=obj.end,
                                                                   end__lte=self.end)
        if 'start' in changed_attrs and 'end' in changed_attrs:
            pending_shifts = prev_object_related_shifts
            # Сдвинули начало влево (увеличили интервал), ищем смены больше start
            if getattr(self, 'start') < getattr(obj, 'start'):
                pending_shifts = pending_shifts.filter(start__gte=self.start,
                                                       start__lt=obj.start)
            # вправо (уменьшили интервал), ищем меньше start
            else:
                pending_shifts = pending_shifts.filter(start__lt=self.start,
                                                       start__gte=obj.start)
            if getattr(self, 'end') < getattr(obj, 'end'):
                pending_shifts = pending_shifts.filter(end__gt=self.end,
                                                       end__lte=obj.end)
            # вправо (увеличили интервал), ищем меньше end
            else:
                pending_shifts = pending_shifts.filter(end__gt=obj.end,
                                                       end__lte=self.end)
        return result

    @property
    def value_total(self):
        return self.value + self.value_ext

    def max_value(self, month):
        """ Возвращает максимальное количество квот"""
        max_value = "-"
        affected_quota_volume = self.get_affected_quota_volume(month)
        if affected_quota_volume:
            max_value = affected_quota_volume.value
        return max_value

    def free_value(self, month):
        """ Возвращает количество свободных квот на заданный месяц"""
        free_value = "-"
        affected_quota_volume = self.get_affected_quota_volume(month)
        if affected_quota_volume:
            max_value = int(affected_quota_volume.value)
            affected_quotas = self.get_similar_area_quotas(month)
            affected_value = affected_quotas.aggregate(sum=Sum(F('value') + F('value_ext'))).get("sum", 0)
            if affected_quotas.exists():
                free_value = max_value - affected_value
        return free_value

    def get_quota_info(self, month):
        return QuotaInfo.objects.filter(quota=self, month=month)

    def shifts_count(self, month):
        quota_info = self.get_quota_info(month).aggregate(total=Sum('shifts_count'))
        return quota_info['total']

    def open_shifts_count(self, month):
        quota_info = self.get_quota_info(month).aggregate(total=Sum('shifts_count'), open=Sum('open_shifts_count'))
        return quota_info['open']


class QuotaInfo(models.Model):
    quota = models.ForeignKey(Quota, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Квота')
    quota_number = models.PositiveIntegerField(verbose_name='Номер квоты', default=0)
    shifts_count = models.PositiveIntegerField(verbose_name='Количество смен', default=0)
    open_shifts_count = models.PositiveIntegerField(verbose_name='Количество открытых смен', default=0)
    month = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False, verbose_name="Месяц")
    dt_updated = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name="Обновлена")

    class Meta:
        verbose_name = 'Информация по квоте'
        verbose_name_plural = 'Информация по квоте'

    def __str__(self):
        return "{0} / {1}".format(self.quota, self.month)

    def modification_count(self, set_open_count, set_count):
        """
        Изменение
        :param setter_open_count:
        :param setter_count:
        :return:
        """
        QuotaInfo.objects.filter(pk=self.pk).update(open_shifts_count=F('open_shifts_count') + set_open_count,
                                                    shifts_count=F('shifts_count') + set_count)


'''
Изменения данных QuotaInfo
по сигналам от PromoShifts
'''


@receiver(pre_delete, sender='shifts.PromoShift')
def quota_info_promo_shift_delete_callback(sender, **kwargs):
    """
    Изменение данных при жестком удалении обекта
    :param sender:
    :param shift: PromoShift
    :return:
    """
    shift = kwargs.get('instance')
    if shift.quota_info:
        shift_count = -1
        if not shift.agency_employee:
            shift_open_count = -1
        shift.quota_info.modification_count(shift_open_count, shift_count)


@receiver(promo_shift_change_signal)
def quota_info_promo_shift_change_callback(sender, old_shift, new_shift, **kwargs):
    """
    Изменение QuoteInfo при изменении shift
    :param sender:
    :param kwargs:
    :return:
    """
    from apps.shifts.methods import get_or_create_quota_info
    from apps.shifts.models import PromoShift
    new_shift.quota_info = get_or_create_quota_info(new_shift)
    new_shift_count = 0
    new_shift_open_count = 0
    old_shift_count = 0
    old_shift_open_count = 0

    PromoShift.objects.filter(pk=new_shift.pk).update(quota_info=new_shift.quota_info)
    if not old_shift:
        # created PromoShift
        # когда создаю
        if new_shift.state != 'delete':
            new_shift_count += 1
            if not new_shift.agency_employee:
                new_shift_open_count += 1
    else:
        # редактирование

        if old_shift.quota_info != new_shift.quota_info:
            # если QuotaInfo поменялась уменьшаю старую квоту
            if old_shift.quota_info and old_shift.state != 'delete':
                old_shift_count -= 1
                if not old_shift.agency_employee:
                    old_shift_open_count -= 1
                old_shift.quota_info.modification_count(old_shift_open_count, old_shift_count)
            # увеличиваем новую квоту
            if new_shift.state != 'delete':
                new_shift_count += 1
                if not new_shift.agency_employee:
                    new_shift_open_count += 1

        else:
            # если QuotaInfo не поменялась
            if old_shift.state == 'delete' and new_shift.state != 'delete':
                new_shift_count += 1
                if not new_shift.agency_employee:
                    new_shift_open_count += 1
            elif old_shift.state != 'delete' and new_shift.state == 'delete':
                new_shift_count -= 1
                if not new_shift.agency_employee:
                    new_shift_open_count -= 1
            # установка и удоление сотрудника со смены
            elif old_shift.agency_employee is None and new_shift.agency_employee:
                new_shift_open_count -= 1
            elif old_shift.agency_employee and new_shift.agency_employee is None:
                new_shift_open_count += 1
    if new_shift.quota_info.open_shifts_count < 0:
        print('error open', new_shift.quota_info.open_shifts_count)
        new_shift.quota_info.open_shifts_count = 0
    if new_shift.quota_info.shifts_count < 0:
        print('error shift', new_shift.quota_info.shifts_count)
        new_shift.quota_info.shifts_count = 0
    try:
        new_shift.quota_info.modification_count(new_shift_open_count, new_shift_count)
    except Exception:
        print('отрицательный')

    new_shift.quota_info.refresh_from_db()
    print('new', new_shift.quota_info.open_shifts_count, new_shift.quota_info.shifts_count)


# @TODO куда относится этот сигнал??
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
