#
# Copyright 2018 ООО «Верме»
#
# Файл моделей сотрудников
#

from django.db import models
from django.db.models import Q
import uuid
import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from apps.outsource.models import Headquater, Organization, Agency, Job
from .signals import *
from django.dispatch import receiver

EVENT_KIND_CHOICES = (  # возможные состояния обработки событий (EmployeeEvent)
    ("recruitment", "Recruitment"),
    ("dismissal", "Dismissal"),
    ("change", "Change"),
    ("agency", "Agency"),
)

EVENT_HISTORY_KIND_CHOICES = (  # возможные состояния обработки событий (EventHistory)
    ("accept_recruitment", "Accept"),
    ("reject_recruitment", "Reject"),
    ("dismissal", "Dismissal"),
)

GENDER_CHOICES = (  # возможный пол (AgencyEmployee)
    ("male", "Мужской"),
    ("female", "Женский"),
)

STATE_CHOICES = (  # возможный статус (EmployeeHistory)
    ("active", "Активен"),
    ("inactive", "Неактивен"),
)

DOC_TYPE_CHOICES = (  # возможные коды документов (DocType)
    ("medical", "Мед. книжка"),
    ("other", "Другой"),
)


class AgencyEmployee(models.Model):
    """Сотрудники агентства"""
    number = models.CharField(max_length=250, blank=False, null=False,
                              verbose_name='Табельный номер сотрудника в агентстве')
    firstname = models.CharField(max_length=250, blank=False, null=False, verbose_name='Имя')
    surname = models.CharField(max_length=250, blank=False, null=False, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=250, blank=True, null=False, verbose_name='Отчество')
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES, default=GENDER_CHOICES[0][0],
                              blank=False, null=False, verbose_name="Пол")
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                                     verbose_name="Дата рождения")
    place_of_birth = models.CharField(max_length=250, blank=True, null=True, verbose_name='Место рождения')
    agency = models.ForeignKey(Agency, blank=False, null=False, on_delete=models.PROTECT, verbose_name="Агентство")
    receipt = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                               verbose_name="Дата приема")
    dismissal = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                                 verbose_name="Дата увольнения")
    last_external_update = models.DateTimeField(
        verbose_name="Последнее обновление через API", blank=True, null=True)

    class Meta:
        unique_together = ("number", "agency")
        verbose_name_plural = "Сотрудники"
        verbose_name = "Сотрудник"

    def get_history(self):
        return self.ae_history.distinct('agency').values_list('agency', flat=True)

    def save(self, *args, **kwargs):
        obj = None
        if self.pk:
            obj = AgencyEmployee.objects.filter(pk=self.pk).first()
        super(AgencyEmployee, self).save(*args, **kwargs)
        edit_agency_employee_signal.send(self.__class__, old_agency_employee=obj, new_agency_employee=self)

    def get_diff(self, obj):
        if obj is None:
            obj = AgencyEmployee()

        if not isinstance(obj, AgencyEmployee):
            raise Exception("AgencyEmployee.get_diff can apply only AgencyEmployee object")

        result = {}
        for attr in ['agency', 'number', 'receipt', 'dismissal']:
            if getattr(self, attr) != getattr(obj, attr):
                result.update({
                    attr: {'from': getattr(obj, attr), 'to': getattr(self, attr)}
                })

        return result

    @property
    def name(self):
        return ''.join(
            [self.surname, ' ', self.firstname, ' ', self.patronymic])

    @property
    def external_number(self):
        org_history = OrgHistory.objects.filter(agency_employee=self).order_by('-id').first()
        if org_history:
            return org_history.number
        return None

    def last_medical(self):
        medical = self.documents().filter(doc_type__code='medical').order_by('-end').first()
        return medical

    @property
    def last_medical_guid(self):
        medical = self.last_medical()
        if medical:
            return str(medical.guid)
        return None

    @property
    def medical_end_date(self):
        medical = self.last_medical()
        if medical:
            return medical.end
        return None

    @property
    def jobs_export(self):
        job_sets = JobHistory.objects.values_list('job', flat=True).filter(agency_employee=self)
        return ",".join(["".join(i) for i in Job.objects.values_list('name').filter(pk__in=set(job_sets))])

    @property
    def agencies_export(self):
        agency_sets = AgencyHistory.objects.values_list('agency', flat=True).filter(agency_employee=self)
        return ",".join(["".join(i) for i in Agency.objects.values_list('name').filter(pk__in=set(agency_sets))])

    @property
    def headquarters_export(self):
        headquarter_sets = OrgHistory.objects. \
            filter(Q(agency_employee=self, start__lte=timezone.now().date()) & (
                Q(end__gte=timezone.now().date()) | Q(end__isnull=True))). \
            order_by('headquater_id'). \
            distinct('headquater_id').values_list('headquater_id', flat=True)
        return ",".join(
            ["".join(i) for i in Headquater.objects.values_list('name').filter(pk__in=set(headquarter_sets))])

    @property
    def organizations_export(self):
        return ",".join(["".join(i) for i in self.get_organizations().values_list('organization__name', flat=True)])

    @property
    def cities_export(self):
        return ",".join(["".join(i) for i in self.get_cities().values_list('organization__name', flat=True)])

    def jobs(self):
        """Список функций сотрудника"""
        job_sets = JobHistory.objects.values_list('job', flat=True).filter(agency_employee=self)
        return ",".join(["".join(i) for i in Job.objects.values_list('name').filter(pk__in=set(job_sets))])

    jobs.short_description = "Функции"
    jobs.allow_tags = True  # для обработки "<br>" в list_display (вывод в столбик)

    def agencies(self):
        """Список агентств сотрудника."""
        agency_sets = AgencyHistory.objects.values_list('agency', flat=True).filter(agency_employee=self)
        return "<br>".join(["".join(i) for i in Agency.objects.values_list('name').filter(pk__in=set(agency_sets))])

    agencies.short_description = "Агентства"
    agencies.allow_tags = True  # для обработки "<br>" в list_display (вывод в столбик)

    def headquaters(self):
        """Список организаций сотрудника."""
        headquater_sets = OrgHistory.objects.filter(agency_employee=self,
                                                    start__lte=timezone.now().date()) \
            .order_by('headquater_id'). \
            distinct('headquater_id').values_list('headquater_id', flat=True)
        return headquater_sets

    def documents(self):
        """Список документов сотрудника."""
        return EmployeeDoc.objects.filter(agency_employee=self).select_related('doc_type')

    def __str__(self):
        return self.name

    @property
    def has_violations(self):
        # TODO убрать, перенесено
        """Проверка наличия хотя бы одного нарушения"""
        return self.check_violations_by_date()

    def get_client_start(self, headquarter):
        """ Возвращает дату начала работы у клиента """
        org_history = OrgHistory.objects.filter(agency_employee=self, end__isnull=True,
                                                headquater=headquarter). \
            order_by('-start').first()
        return org_history.start if org_history else None

    def get_client_end(self, headquarter):
        """ Возвращает последнюю дату окончания работы у клиента """
        org_history = OrgHistory.objects.filter(agency_employee=self, end__isnull=False,
                                                headquater=headquarter). \
            order_by('-end').first()
        return org_history.end if org_history else None

    def get_organizations(self):
        """Организации в которых работает/работал сотрудник (история организаций)"""
        return OrgHistory.objects.filter(agency_employee=self, end__isnull=True).order_by(
            'organization__name').distinct('organization__name').values('number',
                                                                        'organization__name',
                                                                        'organization__headquater__name',
                                                                        'organization__headquater__short')

    def get_cities(self):
        """Города в которых работает/работал сотрудник (история организаций)"""
        return OrgHistory.objects.filter(agency_employee=self, end__isnull=True, organization__kind='city').order_by(
            'organization__name').distinct('organization__name').values('number',
                                                                        'organization__name',
                                                                        'organization__headquater__name',
                                                                        'organization__headquater__short')

    def open_recruitment_events(self):
        """Открытые мероприятитя приема, на которые еще не поступил ответ"""
        return EmployeeEvent.objects.filter(agency_employee=self,
                                            kind='recruitment',
                                            answer_received=False). \
            order_by('organization_id', 'dt_created')

    def get_open_recruitment_events(self):
        """Открытые мероприятитя приема, на которые еще не поступил ответ"""
        return self.open_recruitment_events().distinct('organization_id').values('headquater__name',
                                                                                 'headquater__short',
                                                                                 'organization__name')

    def get_closed_orghistory(self, date=None):
        """Закрытые OrgHistory сотрудника на дату"""
        if not date:
            date = timezone.now().date()
        end_date = date - datetime.timedelta(days=1)
        return OrgHistory.objects.filter(agency_employee=self,
                                         end__gte=end_date). \
            order_by('organization__name').distinct('organization__name').values('organization__name',
                                                                                 'organization__headquater__name',
                                                                                 'organization__headquater__short')

    def get_number_in_organization(self, headquarter, day=None):
        """Метод возвращает табельный номер сотрудника, назначенный ему в организации headquarter и действующий на день day"""
        query = OrgHistory.objects.filter(headquater=headquarter, agency_employee=self, is_inactive=False)
        if day:
            query = query.filter(Q(start__lte=day) & (Q(end__gte=day) | Q(end__isnull=True)))
        org_history = query.last()
        if not org_history:
            return None
        return org_history.number

    def get_jobs_list_by_date(self, date=None):
        """ВОзвращает список функций сотрудника на дату"""
        if not date:
            date = timezone.now().date()
        jobs_list_by_date = JobHistory.objects.filter(Q(agency_employee=self),
                                                      Q(start__lte=date), Q(end__gte=date) | Q(end__isnull=True)) \
            .order_by('job__name').distinct('job__name').values_list('job__name', flat=True)
        return jobs_list_by_date

    def get_orgs_list_by_headquarter(self, headquater=None):
        """Возвращает список организаций компании клиента в которых работает сотрудник"""
        orgs_list_by_date = OrgHistory.objects.filter(agency_employee=self, headquater=headquater) \
            .order_by('organization__name') \
            .distinct('organization__name').values_list('organization__name', flat=True)
        return orgs_list_by_date

    def get_closing_orghistories_by_date(self, date=None):
        """Возвращает список Orghistory от текущей даты, у которых указана дата окончания"""
        if not date:
            date = timezone.now().date()
        return OrgHistory.objects.filter(agency_employee=self, end__gte=date)

    def get_blacklisted_events(self):
        """Возвращает список событий сотрудника с флагом blacklist"""
        return EmployeeEvent.objects.filter(agency_employee=self, blacklist=True)

    def latest_shift(self):
        """Возвращает последнюю смену сотрудника"""
        from apps.shifts.models import OutsourcingShift, PromoShift

        # Определение типа смен для поиска
        shifts_type = self.agency.headquater.party

        if shifts_type == 'agency':
            shifts = OutsourcingShift
        else:
            shifts = PromoShift

        latest_shift = shifts.objects.filter(agency_employee=self, state='accept').order_by('-start_date').first()
        return latest_shift


class JobHistory(models.Model):
    """История назначения функций сотруднику"""
    job = models.ForeignKey(Job, blank=False, null=False, on_delete=models.PROTECT, verbose_name="Функция")
    agency_employee = models.ForeignKey(AgencyEmployee, blank=False, null=False, on_delete=models.PROTECT)
    start = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                             verbose_name="С")
    end = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                           verbose_name="По")

    class Meta:
        ordering = ["-start"]
        verbose_name_plural = "История назначений функций"
        verbose_name = "История назначений функций"

    def __str__(self):
        return "{0} / {1} / {2}".format(self.job, self.agency_employee, self.start)


class AgencyHistory(models.Model):
    """История назначения сотрудника агентству"""
    agency = models.ForeignKey(Agency, blank=False, null=False, on_delete=models.CASCADE, verbose_name="Агентство")
    agency_employee = models.ForeignKey(AgencyEmployee, blank=False, null=False, on_delete=models.CASCADE,
                                        related_name='ae_history')
    start = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                             verbose_name="Дата начала")
    end = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                           verbose_name="Дата окончания")

    class Meta:
        ordering = ["-start"]
        verbose_name_plural = "История назначений агентств"
        verbose_name = "История назначений агентств"

    def __str__(self):
        return "{0} / {1} / {2}".format(self.agency, self.agency_employee, self.start)

    def get_agency_to_date(self, start, end):
        """
        массив объектов с датами начала работы и конца
        :param start:
        :param end:
        :return:
        """
        pass


@receiver(edit_agency_employee_signal)
def agency_history_callback(sender, old_agency_employee, new_agency_employee, **kwargs):
    if not old_agency_employee:
        # если новый, то я создаю AgencyHistory
        AgencyHistory(agency_employee=new_agency_employee,start=new_agency_employee.receipt, agency=new_agency_employee.agency).save()
        return True
    else:
        if not old_agency_employee.dismissal and new_agency_employee.dismissal:
            # при увольнении обрабатываю сигнал
            AgencyHistory.objects.filter(end__isnull=True).update(end=new_agency_employee.dismissal)
            if old_agency_employee.agency != new_agency_employee.agency:
                # защита от изменения агенства с одновременны увольнением или обратным приемом
                new_agency_employee.agency = old_agency_employee.agency
                new_agency_employee.save()
        elif not new_agency_employee.dismissal and old_agency_employee.dismissal:
            # вернули на работу, берем максимальную дату и возвращаем
            max_date = AgencyHistory.objects.filter(agency_employee=new_agency_employee).order_by('-end').first()
            if max_date:
                max_date = max_date.end
            if datetime.date.today() > max_date:
                max_date = datetime.date.today()
            AgencyHistory(agency_employee=new_agency_employee,start=max_date + datetime.timedelta(1), agency=new_agency_employee.agency).save()
        elif new_agency_employee.agency != old_agency_employee.agency:
            ah = AgencyHistory.objects.filter(end__isnull=True, agency=new_agency_employee.agency).first()
            if not ah:
                max_date = AgencyHistory.objects.order_by('-end').first()
                if max_date:
                    max_date = max_date.end
                if datetime.date.today() > max_date:
                    max_date = datetime.date.today()
                    ah = AgencyHistory(agency_employee=new_agency_employee, start=max_date + datetime.timedelta(1), agency=new_agency_employee.agency)
                    ah.save()
            from apps.shifts.models import PromoShift, OutsourcingShift
            PromoShift.objects.filter(agency_employee=new_agency_employee, start_date__gte=ah.start).update(
                agency_employee=None)
            OutsourcingShift.objects.filter(agency_employee=new_agency_employee,
                                            start_date__gte=ah.start).update(
                agency_employee=None)


class OrgHistory(models.Model):
    """История назначения организаций"""
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Клиент')
    organization = models.ForeignKey(Organization, blank=False, null=False, on_delete=models.PROTECT,
                                     verbose_name='Организация')
    agency_employee = models.ForeignKey(AgencyEmployee, blank=False, null=False, on_delete=models.PROTECT)
    number = models.CharField(max_length=250, blank=False, null=False,
                              verbose_name='ТН в организации')
    start = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                             verbose_name="Дата приема")
    end = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                           verbose_name="Дата увольнения")
    is_inactive = models.BooleanField(blank=True, verbose_name='Неактивен (проходит обучение)')

    class Meta:
        unique_together = ('number', 'headquater', 'organization', 'start', 'agency_employee')
        ordering = ["-start"]
        verbose_name_plural = "История назначений организаций"
        verbose_name = "История назначений организаций"

    def __str__(self):
        return "{0} / {1} / {2} / {3} /{4}".format(self.organization, self.agency_employee, self.start, self.end, self.number)


class EmployeeEvent(models.Model):
    """История событий"""
    guid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='GUID')
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Пользователь')
    agency_employee = models.ForeignKey(AgencyEmployee, blank=False, null=False, on_delete=models.PROTECT,
                                        verbose_name='Сотрудник')
    agency = models.ForeignKey(Agency, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Агентство')
    dt_created = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name='Создано')
    kind = models.CharField(max_length=16, choices=EVENT_KIND_CHOICES, verbose_name='Вид')
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Клиент')
    organization = models.ForeignKey(Organization, blank=False, null=True, on_delete=models.PROTECT,
                                     verbose_name='Подразделение')
    recruitment_date = models.DateField(auto_now=False, null=True, blank=True, verbose_name='Дата приема сотрудника')
    dismissal_date = models.DateField(auto_now=False, null=True, blank=True, verbose_name='Дата увольнения сотрудника')
    dismissal_reason = models.CharField(max_length=1000, blank=True, verbose_name='Причина увольнения')
    blacklist = models.BooleanField(default=False, null=False, verbose_name='Включен в черный список')
    ext_number = models.CharField(max_length=250, blank=True, verbose_name='ТН в организации')
    answer_received = models.BooleanField(default=False, null=False, verbose_name='Получен ответ на событие')
    params = JSONField(verbose_name='Параметры', default={})

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Кадровые мероприятия"
        verbose_name = "Кадровое мероприятие"

    def __str__(self):
        return "{0} / {1} / {2}".format(self.agency_employee, self.agency, self.dt_created)


class EmployeeHistory(models.Model):
    """История внешних событий"""
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Пользователь')
    dt_created = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name='Создано')
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Клиент')
    organization = models.ForeignKey(Organization, blank=False, null=False, on_delete=models.PROTECT,
                                     verbose_name='Подразделение')
    agency = models.ForeignKey(Agency, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Агентство')
    agency_employee = models.ForeignKey(AgencyEmployee, blank=False, null=False, on_delete=models.PROTECT,
                                        verbose_name='Сотрудник')
    event = models.ForeignKey(EmployeeEvent, blank=True, null=True, on_delete=models.PROTECT, verbose_name='Событие')
    kind = models.CharField(max_length=20, blank=False, null=False, choices=EVENT_HISTORY_KIND_CHOICES,
                            verbose_name='Вид')
    blacklist = models.BooleanField(default=False, null=False, verbose_name='Включен в черный список')
    # Опциональные поля
    ext_number = models.CharField(max_length=250, blank=True, verbose_name='ТН в организации')
    recruitment_date = models.DateField(auto_now=False, null=True, blank=True, verbose_name='Дата приема сотрудника')
    dismissal_date = models.DateField(auto_now=False, null=True, blank=True, verbose_name='Дата увольнения сотрудника')
    dismissal_reason = models.CharField(max_length=1000, blank=True, verbose_name='Причина увольнения')
    reject_reason = models.CharField(max_length=1000, blank=True, null=False, verbose_name='Причина отказа')
    recruitment_state = models.CharField(max_length=8, choices=STATE_CHOICES, default=STATE_CHOICES[0][0], blank=False,
                                         null=False, verbose_name='Статус регистрации')

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Подтверждение кадрового мероприятия"
        verbose_name = "Подтверждение кадрового мероприятия"

    def __str__(self):
        return "{0} / {1}".format(self.agency_employee, self.dt_created)


class DocType(models.Model):
    """Вид документа"""
    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Название')
    code = models.CharField(max_length=250, choices=DOC_TYPE_CHOICES, default=DOC_TYPE_CHOICES[0][0],
                            verbose_name='Код')
    sort_key = models.IntegerField(verbose_name="порядок отображения")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Справочник видов документов"
        verbose_name = "Документ"

    def __str__(self):
        return "{0} / {1}".format(self.name, self.code)


class EmployeeDoc(models.Model):
    """Документ сотрудника"""
    guid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='GUID')
    doc_type = models.ForeignKey(DocType, blank=False, null=False, on_delete=models.PROTECT,
                                 verbose_name='Вид документа')
    agency_employee = models.ForeignKey(AgencyEmployee, blank=False, null=False, on_delete=models.PROTECT,
                                        verbose_name='Сотрудник')
    start = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                             verbose_name="С")
    end = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                           verbose_name="По")
    link = models.CharField(max_length=1000, blank=True, verbose_name='Образец документа')
    comments = models.CharField(max_length=1000, blank=True, verbose_name='Комментарий')
    dt_change = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name="Последнее изменение")
    has_files = models.BooleanField(default=False, verbose_name="Наличие файлов")

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Документы сотрудников"
        verbose_name = "Документ сотрудника"

    def __str__(self):
        return "{0} / {1} / {2}".format(self.agency_employee, self.doc_type, self.start, self.end)


class AgencyManager(models.Model):
    """Менеджер агентства"""
    full_name = models.CharField(max_length=1000, blank=True, null=False, verbose_name='ФИО')
    position = models.CharField(max_length=100, blank=True, null=False, verbose_name='Должность')
    phone = models.CharField(max_length=12, blank=True, null=False, verbose_name='Телефон')
    email = models.EmailField(max_length=100, blank=True, null=False, verbose_name='EMail')
    agency = models.ForeignKey('outsource.Agency', blank=True, null=True, on_delete=models.PROTECT,
                               verbose_name="Агентство", )

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Менеджеры агентств"
        verbose_name = "Менеджер агентства"

    def __str__(self):
        return f"{self.full_name} / {self.phone} / {self.email}"
