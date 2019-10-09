#
# Copyright 2018 ООО «Верме»
#
# Файл моделей нарушений
#

from django.db import models
from django.db.models import Sum
from apps.permission.models import Page
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import timedelta
import datetime
import pytz
from wfm.settings import TIME_ZONE

SEVERITY_CHOICES = (
    ("low", "Низкий"),
    ("medium", "Средний"),
    ("high", "Высокий"),
)

CODE_CHOICES = (
    ("medical", "Наличие мед. книжки"),
    ("blacklist", "Включен в черный список"),
    ("dismissed_by_agency", "Уволен агентством"),
    ("dismissed_by_client", "Уволен клиентом"),
    ("wait_register", "Ожидает регистрации у клиента"),
    ("quota_no_shifts", "Квоты без смен"),
    ("quota_open_shifts", "Квоты с открытыми сменами"),
    ("medical_no_files", "Наличие файлов мед. книжки"),
    ("employee_no_shifts", "Не назначен на смену"),
)


class ViolationRule(models.Model):
    """Нарушения для сотрудников"""
    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Название')
    code = models.CharField(max_length=32, choices=CODE_CHOICES, default=CODE_CHOICES[0][0], blank=False,
                            null=False,  unique=True, verbose_name='Код')
    icon = models.CharField(verbose_name="Иконка", max_length=64, default="exclamation-triangle",
                            help_text="название со страницы https://fortawesome.github.io/Font-Awesome/icons/")
    pages = models.ManyToManyField(Page, verbose_name='страницы', blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Нарушения"
        verbose_name = "Нарушение"

    def __str__(self):
        return "{0} / {1}".format(self.name, self.code)


class ViolationRuleItem(models.Model):
    """Уровни нарушений"""

    rule = models.ForeignKey(ViolationRule, blank=False, null=False, on_delete=models.CASCADE, verbose_name="Нарушение")
    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Название')
    severity = models.CharField(max_length=8, choices=SEVERITY_CHOICES, default=SEVERITY_CHOICES[0][0], blank=False,
                             null=False, verbose_name='Важность')
    value_from = models.IntegerField(blank=False, null=False, verbose_name='Значение от')
    value_to = models.IntegerField(blank=False, null=False, verbose_name='Значение до')
    message = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Сообщение')

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Уровни нарушений"
        verbose_name = "Уровень нарушения"

    def __str__(self):
        return "{0} / {1}".format(self.name, self.severity)

    def check_queryset(self, queryset=None, date=None):
        if not date:
            date = timezone.now().date()
        else:
            if not isinstance(date, datetime.date):
                date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        # и границы дат
        min_find_date = date + timedelta(days=self.value_from)
        max_find_date = date + timedelta(days=self.value_to)

        # ид для поиска по документам
        employee_ids = queryset.values_list('id', flat=True)

        """Обработка в зависимости от кода нарушения"""
        if self.rule.code == 'medical':
            # Проверка наличия действующей мед. книжки
            # Определяем минимальную дату приема с которой медкнижка должна быть
            min_receipt_date = date - timedelta(days=14)
            # сотрудники с даты приема которых прошло более 14 дней
            # которых надо проверять
            more_queryset = queryset.filter(receipt__lte=min_receipt_date)
            # получение мед книжек по сотрудникам у которых она есть и удовлетворяет условиям
            from apps.employees.methods import get_employee_docs
            employee_medical_ids = get_employee_docs(doc_type__code='medical',
                                                     end__gte=min_find_date,
                                                     end__lte=max_find_date,
                                                     agency_employee_id__in=more_queryset.values_list('id', flat=True))
            # мед. книжки которых нет и которые закончились
            if self.value_from == self.value_to == 0:
                # проверка, есть ли вообще мед книжка у сотрудника, для нарушения отсутствует
                employee_medical_ids2 = get_employee_docs(doc_type__code='medical',
                                                          end__gte=max_find_date,
                                                          agency_employee_id__in=more_queryset.values_list('id',
                                                                                                           flat=True))
                delta_ids = list(set(more_queryset.values_list('id', flat=True)) - set(employee_medical_ids))
                queryset = queryset.filter(id__in=list(employee_medical_ids)+list(delta_ids)).\
                    exclude(id__in=employee_medical_ids2)
            # остальные условия
            else:
                queryset = queryset.filter(id__in=employee_medical_ids)

        if self.rule.code == 'blacklist':
            # Проверка событий EmployeeEvent с флагом включения в blacklist
            from apps.employees.methods import get_employee_events
            employee_blacklisted_ids = get_employee_events(agency_employee_id__in=employee_ids,
                                                                    blacklist=True)
            queryset = queryset.filter(id__in=employee_blacklisted_ids)

        # TODO пока оставляем, но правило не используем
        if self.rule.code == 'dismissed_by_agency':
            # Проверка даты увольенения сотрудника из агентства
            # сотрудники с даты приема которых прошло менее 14 дней
            queryset = queryset.filter(dismissal__gte=min_find_date, dismissal__lte=max_find_date)

        # TODO пока оставляем, но правило не используем
        if self.rule.code == 'dismissed_by_client':
            # Проверка наличия заканчивающихся авторизаций у клиента
            from apps.employees.methods import get_employee_orghistories
            employee_closing_ids = get_employee_orghistories(agency_employee_id__in=employee_ids,
                                                             end__gte=min_find_date,
                                                             end__lte=max_find_date)
            queryset = queryset.filter(id__in=employee_closing_ids)

        if self.rule.code == 'wait_register':
            from apps.employees.methods import get_employee_events
            # Проверка событий приема, на которые не поступил ответ
            min_find_date = date - timedelta(days=self.value_to)
            max_find_date = date - timedelta(days=self.value_from)
            min_find_dtime = make_aware(datetime.datetime.combine(min_find_date, datetime.datetime.min.time()),
                                        timezone=pytz.timezone(TIME_ZONE))
            max_find_dtime = make_aware(datetime.datetime.combine(max_find_date, datetime.datetime.max.time()),
                                        timezone=pytz.timezone(TIME_ZONE))
            employee_wait_ids = get_employee_events(agency_employee_id__in=employee_ids,
                                                    kind='recruitment',
                                                    answer_received=False,
                                                    dt_created__gte=min_find_dtime,
                                                    dt_created__lte=max_find_dtime)
            queryset = queryset.filter(id__in=employee_wait_ids)

        if self.rule.code == 'quota_no_shifts':
            # Поиск квот, по которым нет смен
            from apps.outsource.models import QuotaInfo
            # По которым есть QuotaInfo (с любыми значениями, просто наличие)
            exists_quota_infos = QuotaInfo.objects.filter(month=date, quota__in=queryset).\
                order_by('quota_id').distinct('quota_id').values_list('quota_id', flat=True)
            # По которым вообще нет QuotaInfo
            not_exists_quota_infos = queryset.exclude(id__in=exists_quota_infos).values_list('id', flat=True)

            # Далее непосредственно проверка условий
            if self.value_from == 1 and self.value_to == 1:
                # Вариант: нет смен
                # либо нет quota_info, либо аггрегированная сумма shifts_count за месяц равна 0
                # Проверка условия
                quota_infos = QuotaInfo.objects.filter(month=date, quota__in=exists_quota_infos).\
                    values('quota_id').annotate(total=Sum('shifts_count')).filter(total=0).values_list('quota_id', flat=True)
                queryset = queryset.filter(id__in=list(list(quota_infos) + list(not_exists_quota_infos)))
            else:
                # Вариант: есть смены
                # обязательно наличие quota_info + аггрегированная сумма shifts_count за месяц больше 0
                # Проверка условия
                quota_infos = QuotaInfo.objects.filter(month=date, quota_id__in=exists_quota_infos, shifts_count__gt=0)\
                    .order_by('quota_id').distinct('quota_id').values_list('quota_id')
                queryset = queryset.filter(id__in=quota_infos)

        if self.rule.code == 'quota_open_shifts':
            # Поиск квот, по которым нет назначенных на смены сотрудников
            from apps.outsource.models import QuotaInfo
            quota_ids = set()
            quota_infos = QuotaInfo.objects.filter(month=date, quota__in=queryset, shifts_count__gt=0)
            for q_i in quota_infos:
                if q_i.open_shifts_count > 0:
                    quota_ids.add(q_i.quota_id)
            queryset = queryset.filter(id__in=quota_infos.values_list('quota_id', flat=True))
            if self.value_from == 1 and self.value_to == 1:
                queryset = queryset.filter(id__in=quota_ids)
            else:
                queryset = queryset.exclude(id__in=quota_ids)

        if self.rule.code == 'medical_no_files':
            from apps.employees.methods import get_employee_docs
            if self.value_from == 0 and self.value_to == 0:
                flag = False
            else:
                flag = True
            employee_medical_ids = get_employee_docs(doc_type__code='medical',
                                                     has_files=flag,
                                                     agency_employee_id__in=employee_ids)

            queryset = queryset.filter(id__in=employee_medical_ids)

        if self.rule.code == 'employee_no_shifts':
            from apps.shifts.models import OutsourcingShift, PromoShift
            if queryset:
                # Определение типа смен для поиска
                shifts_type = queryset[:1][0].agency.headquater.party
                if shifts_type == 'agency':
                    shifts = OutsourcingShift
                else:
                    shifts = PromoShift

                # Интервалы поиска по периоду
                min_find_date = date - timedelta(days=self.value_to)
                max_find_date = date - timedelta(days=self.value_from)

                # Поиск всех смен
                shifts = shifts.objects.filter(state='accept')#.all()

                # Фильтрация смен по периоду
                shifts = shifts.filter(start_date__gte=min_find_date)
                # Получаем те, в которых сотрудники присутствуют в первоначальной выборке
                shifts = shifts.filter(agency_employee_id__in=queryset.values_list('id', flat=True))
                # Идентификаторы сотрудников, которые назначены на смену
                shifts = shifts.\
                    order_by('agency_employee_id').\
                    distinct('agency_employee_id')

                employee_shift_ids = shifts.values_list('agency_employee_id', flat=True)
                queryset = queryset.exclude(id__in=employee_shift_ids)

        return queryset
