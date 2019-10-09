#
# Copyright 2018 ООО «Верме»
#
# Файл моделей прав доступа
#
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from gfklookupwidget.fields import GfkLookupField

from apps.outsource.models import Headquater, Agency, Organization
from apps.lib.utils import content_type_Q_for_models
from apps.lib.forms import PageChoiceField

PARTY_CHOICES = (
    ("agency", "Агентство"),
    ("client", "Клиент"),
    ("promo", "Промоутер"),
    ("broker", "Кредитный брокер"),
)

ACTION_CHOICES = (
    ("read", "Чтение"),
    ("write", "Запись"),
)


DATE_CHANGER_CHOICES = (
    ("disabled", "Отключен"),
    ("month", "Месяц"),
    ("week", "Неделя"),
)

class Page(models.Model):
    """ Страница """
    name = models.CharField(verbose_name="название", max_length=128)
    code = PageChoiceField(verbose_name="код")
    party = models.CharField(verbose_name='тип', max_length=8, choices=PARTY_CHOICES, blank=False, null=False)
    icon = models.CharField(verbose_name="иконка", max_length=64, default="warning",
                            help_text="название со страницы https://fortawesome.github.io/Font-Awesome/icons/")
    ext_name = models.TextField(verbose_name="длинное название", blank=True)
    disabled = models.BooleanField(verbose_name="страница неактивна", default=False)
    sort_key = models.IntegerField(verbose_name="порядок отображения")
    is_hidden = models.BooleanField(verbose_name="страница скрыта", default=False)
    parent = models.ForeignKey("self", models.CASCADE, null=True, blank=True, verbose_name="страница")
    date_changer_mode = models.CharField(verbose_name='переключатель периодов', max_length=8,
                                         choices=DATE_CHANGER_CHOICES, default=DATE_CHANGER_CHOICES[0][0],
                                         blank=False, null=False)

    def __str__(self):
        return f"{self.party} / {self.name}"

    @property
    def children(self):
        return Page.objects.filter(parent=self, is_hidden=False)

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'


class AccessRole(models.Model):
    """ Роль """
    name = models.CharField(verbose_name="название", max_length=128)
    code = models.CharField(verbose_name="код", max_length=32, blank=False, null=False, unique=True)
    party = models.CharField(verbose_name="тип", max_length=8, choices=PARTY_CHOICES, blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


class Permission(models.Model):
    """ Разрешение """
    action = models.CharField(verbose_name='действие', max_length=8, choices=ACTION_CHOICES,
                              default=ACTION_CHOICES[0][0], blank=False, null=False)
    page = models.ForeignKey(Page, blank=False, null=False, on_delete=models.PROTECT, verbose_name="страница")
    role = models.ForeignKey(AccessRole, blank=False, null=False, on_delete=models.PROTECT, verbose_name="роль")

    def __str__(self):
        return f"{self.role} / {self.page} / {self.action}"

    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'


class AccessProfile(models.Model):
    """ Права доступа """
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT,
                                   verbose_name="компания", related_name='acc_prof_to_headquater')
    role = models.ForeignKey(AccessRole, blank=False, null=False, on_delete=models.PROTECT, verbose_name="роль")
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.PROTECT,
                             verbose_name="пользователь", related_name='acc_prof_to_user')
    unit_type_choices = content_type_Q_for_models(Agency, Organization)
    unit_type = models.ForeignKey(ContentType, models.CASCADE, limit_choices_to=unit_type_choices,
                                  verbose_name='тип орг. единицы')
    unit_id = GfkLookupField('unit_type', verbose_name="орг. единица")
    unit = GenericForeignKey('unit_type', 'unit_id')

    def __str__(self):
        return f"{self.headquater} / {self.role} / {self.user} / {self.unit}"

    class Meta:
        verbose_name = 'Права доступа'
        verbose_name_plural = 'Права доступа'
