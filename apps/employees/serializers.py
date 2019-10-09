#
# Copyright 2018 ООО «Верме»
#
# Файл serializers сотрудников для django_rest_framework
# Используется для методов апи
# Для работы нужен rest_framework
#

import re
from datetime import date
from copy import copy
from django.utils import timezone
from rest_framework import serializers
from .models import *
from .methods import *
from apps.outsource.models import Agency, Organization, Job
from apps.outsource.serializers import OrganizationSerializer3, OrganizationSerializer, HeadquaterSerializer


class OrgHistorySerializer(serializers.ModelSerializer):
    """Назначения организаций"""
    agency_employee_id = serializers.PrimaryKeyRelatedField(queryset=AgencyEmployee.objects.all(),
                                                            write_only=True, allow_null=False)
    organization = OrganizationSerializer3(many=False, read_only=True, allow_null=True)
    organization_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(),
                                                         write_only=True, allow_null=False)

    class Meta:
        model = OrgHistory
        fields = ('id', 'agency_employee_id', 'organization', 'organization_id', 'number', 'start', 'end', 'is_inactive')


class EmployeeEventSerializer(serializers.ModelSerializer):
    """Внутренние кадровые мероприятия"""
    organization = OrganizationSerializer(many=False, read_only=True)
    headquater = HeadquaterSerializer(many=False, read_only=True)
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')

    class Meta:
        model = EmployeeEvent
        fields = ('guid', 'headquater', 'organization', 'user', 'kind', 'dt_created', 'recruitment_date', 'ext_number',
                  'dismissal_date', 'dismissal_reason', 'blacklist')


class EmployeeHistorySerializer(serializers.ModelSerializer):
    """Внешние кадровые мероприятия"""
    organization = OrganizationSerializer(many=False, read_only=True)
    headquater = HeadquaterSerializer(many=False, read_only=True)
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')

    class Meta:
        model = EmployeeHistory
        fields = ('headquater', 'organization', 'user', 'kind', 'dt_created', 'recruitment_date', 'ext_number',
                  'dismissal_date', 'dismissal_reason', 'reject_reason', 'blacklist')


"""**************************** СОТРУДНИКИ ***********************************"""


class AgencyEmployeeListRequestSerializer(serializers.Serializer):
    """ Данные запроса по списку сотрудников """
    orgunit = serializers.CharField(max_length=255)
    date = serializers.DateField(required=False)
    month = serializers.DateField(required=False)
    agency_id = serializers.IntegerField(required=False)
    headquarter_id = serializers.IntegerField(required=False)
    aheadquarter_id = serializers.IntegerField(required=False)
    violation_ids = serializers.CharField(max_length=300, default='[]', allow_blank=True)
    # @TODO фикс на неправильный запрос
    state = serializers.ChoiceField((('0', "Все"), ('all', "Все"), ('active', "Работает"), ('dismissed', "Уволен")),
                                    allow_blank=True, default='0')
    medical_export = serializers.BooleanField(default=False)
    xlsexport = serializers.BooleanField(default=False)
    xlsexport_code = serializers.CharField(max_length=255, required=False)


class AgencyEmployeeListResponseSerializer(serializers.Serializer):
    """ Данные ответа по списку сотрудников """
    meta = serializers.JSONField()
    data = serializers.ListField()
    violations_list = serializers.ListField()
    agency_list = serializers.ListField()


class AgencyEmployeeListSerializer(serializers.ModelSerializer):
    """ Список сотрудников """
    text = serializers.CharField(source='name')

    class Meta:
        model = AgencyEmployee
        fields = ('id', 'text')
        read_only_fields = ('id', 'text')


class AgencyEmployeeSerializer(serializers.ModelSerializer):
    """ Минимальный набор данных по сотрудникам """

    class Meta:
        model = AgencyEmployee
        fields = ('id', 'name', 'number')


class AgencyEmployeeReadSerializer(serializers.ModelSerializer):
    """ Чтение данных из карточки сотрудника """
    agency = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    violations = serializers.ListField(default=[])

    class Meta:
        model = AgencyEmployee
        fields = (
            'id', 'number', 'surname', 'firstname', 'patronymic', 'gender', 'date_of_birth', 'place_of_birth', 'agency',
            'agency_id', 'receipt', 'dismissal', 'external_number', 'medical_end_date', 'violations')
        read_only_fields = (
            'id', 'number', 'surname', 'firstname', 'patronymic', 'gender', 'date_of_birth', 'place_of_birth', 'agency',
            'agency_id', 'receipt', 'dismissal', 'external_number', 'medical_end_date', 'violations')


class AgencyEmployeeWriteSerializer(serializers.ModelSerializer):
    """ Сохранение данных в карточку сотрудника """
    #просто атрибуты обкт.атрибут
    __slots__ = ('current_user', 'agency_pages')

    agency_id = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all(), source='agency', allow_null=False)

    class Meta:
        model = AgencyEmployee
        fields = ('id', 'number', 'surname', 'firstname', 'patronymic', 'gender', 'date_of_birth', 'place_of_birth',
                  'agency_id', 'receipt', 'dismissal')
        validators = []


    def validate(self, data):

        if 'agency_employee_id' in self.initial_data:

            instance = open_employee(self.initial_data['agency_employee_id'])
        else:

            instance = None
        # Проверка уникальности внутреннего табельного номера
        employees = employees_by_number(data['agency'], data['number'])

        if employees.exists() and not (instance and instance in employees):
            raise serializers.ValidationError("Поле ТН должно быть уникальным для всех сотрудников агентства")
        # Проверка уникальности по ФИО
        employees = employees_duplicates(data['receipt'], data['surname'], data['firstname'], data['patronymic'],
                                         data['date_of_birth'])

        if employees.count() > 1:
            message = get_emp_id(employees, self.current_user, self.agency_pages)
            raise serializers.ValidationError(
                f"Карточка сотрудника уже существует в агентстве \"{str(data['agency'])}\"  c {str(data['receipt'])}  {str(message)} </a>")
        elif employees.count() == 1 and not (instance and instance in employees):
            message = get_emp_id(employees, self.current_user, self.agency_pages)
            raise serializers.ValidationError(
                f"Карточка сотрудника уже существует в агентстве \"{str(data['agency'])}\"  c {str(data['receipt'])}  {str(message)} </a>")
        # Дата увольнения не может быть 
        if data.get('dismissal', None) and data['dismissal'] < data['receipt']:
            raise serializers.ValidationError("Дата увольнения не может быть ранее даты приема")
        # Возраст сотрудника должен быть 18 лет и более на дату приема
        years = data['receipt'].year - data['date_of_birth'].year
        new_year_day_birth = date(year=data['date_of_birth'].year, month=1, day=1)
        new_year_day_receipt = date(year=data['receipt'].year, month=1, day=1)
        birth_day_of_year = (data['date_of_birth'] - new_year_day_birth).days + 1
        receipt_day_of_year = (data['receipt'] - new_year_day_receipt).days + 1
        if not ((birth_day_of_year <= receipt_day_of_year and years == 18) or years > 18):
            raise serializers.ValidationError("Возраст сотрудника на момент принятия меньше 18 лет")
        # Все проверки выполнены успешно
        return data

    def ru_check(self, value):
        """Проверяет, что значение написано кириллицей"""
        if value == '':
            return value
        match = re.match("""^[а-яА-ЯёЁ]+-?\s?[а-яА-ЯёЁ]+$""", value.lower())
        if not bool(match):
            raise serializers.ValidationError("Поле должно быть написано кириллицей")
        return value

    def validate_surname(self, value):
        """Проверяет что фамилия написана кириллицей"""
        self.ru_check(value)
        return value

    def validate_firstname(self, value):
        """Проверяет что имя написано кириллицей"""
        self.ru_check(value)
        return value

    def validate_patronymic(self, value):
        """Проверяет что отчество написано кириллицей"""
        self.ru_check(value)
        return value

    def validate_date_of_birth(self, value):
        """Проверяет что сотруднику 18+ лет"""
        today = timezone.now().date()
        years = today.year - value.year

        new_year_day_value = date(year=value.year, month=1, day=1)
        new_year_day_current = date(year=today.year, month=1, day=1)
        value_day_of_year = (value - new_year_day_value).days + 1
        today_day_of_year = (today - new_year_day_current).days + 1

        if not ((value_day_of_year <= today_day_of_year and years == 18) or years > 18):
            raise serializers.ValidationError("Возраст сотрудника меньше 18 лет")
        return value

    def update(self, instance, data, current_user):
        """Обновление данных по сотруднику"""
        # Меняем значения основных полей
        is_changed = False
        previous_instance = copy(instance)
        for attr_name in ['number', 'surname', 'firstname', 'patronymic', 'gender', 'date_of_birth', 'place_of_birth']:
            attr_value = data.get(attr_name, getattr(instance, attr_name))
            if getattr(instance, attr_name) != attr_value:
                setattr(instance, attr_name, attr_value)
                is_changed = True
        if is_changed:
            on_change_employee(current_user, instance, 'change', timezone.now().date(), previous_instance)

        # Меняем привязку к агентству
        is_changed = False
        previous_instance = copy(instance)
        for attr_name in ['agency', 'receipt', 'dismissal']:
            attr_value = data.get(attr_name, getattr(instance, attr_name))
            if getattr(instance, attr_name) != attr_value:
                setattr(instance, attr_name, attr_value)
                is_changed = True
        if is_changed:
            on_change_employee(current_user, instance, 'agency', timezone.now().date(), previous_instance)

        # Сохраняем изменения
        instance.save()
        return instance


"""**************************** ДОЛЖНОСТИ СОТРУДНИКА ***********************************"""


class JobHistoryReadSerializer(serializers.ModelSerializer):
    """ Назначения функций (чтение)"""
    job = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    job_id = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all(), source='job')

    class Meta:
        model = JobHistory
        fields = ('id', 'agency_employee_id', 'job', 'job_id', 'start', 'end')
        read_only_fields = ('id', 'agency_employee_id', 'job', 'job_id', 'start', 'end')


class JobHistoryWriteSerializer(serializers.ModelSerializer):
    """Назначения функций запись"""
    agency_employee_id = serializers.PrimaryKeyRelatedField(queryset=AgencyEmployee.objects.all(), allow_null=False,
                                                            source='agency_employee')
    job_id = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all(), allow_null=False, source='job')

    class Meta:
        model = JobHistory
        fields = ('id', 'agency_employee_id', 'job_id', 'start', 'end')

    def validate(self, data):
        # Дата начала и окончания
        start = data.get('start')
        end = data.get('end')
        employee = data['agency_employee']
        if not start:
            raise serializers.ValidationError({"start": "Необходимо заполнить дату начала действия должности"})
        if employee.receipt > start:
            raise serializers.ValidationError("Дата назначения должности не может быть меньше даты приема сотрудника")
        if end and start > end:
            raise serializers.ValidationError("Дата окончания должности не может быть ранее даты начала")
        return data

    def update(self, instance, validated_data, current_user):
        # Корректируем значения полей
        for attr_name in ['agency_employee', 'job', 'start', 'end']:
            setattr(instance, attr_name, validated_data.get(attr_name, getattr(instance, attr_name)))
        # Сохраняем изменения
        instance.save()
        return instance

    def create(self, validated_data, current_user):
        # Создаем новый объект
        return JobHistory.objects.create(**validated_data)


"""**************************** ДОКУМЕНТЫ СОТРУДНИКА ***********************************"""


class DocTypeSerializer(serializers.ModelSerializer):
    """Виды документов"""

    class Meta:
        model = DocType
        fields = ('id', 'name')


class EmployeeDocReadSerializer(serializers.ModelSerializer):
    """Документы сотрудника (чтение)"""
    doc_type = DocTypeSerializer(many=False)
    text = serializers.CharField(source='comments')

    class Meta:
        model = EmployeeDoc
        fields = ('id', 'guid', 'doc_type', 'start', 'end', 'text', 'has_files')
        read_only_fields = ('id', 'guid', 'doc_type', 'start', 'end', 'text', 'has_files')


class EmployeeDocWriteSerializer(serializers.ModelSerializer):
    """ Документы сотрудника (изменение) """
    agency_employee_id = serializers.PrimaryKeyRelatedField(queryset=AgencyEmployee.objects.all(), allow_null=False,
                                                            source='agency_employee')
    doc_type_id = serializers.PrimaryKeyRelatedField(queryset=DocType.objects.all(), allow_null=False,
                                                     source='doc_type')
    text = serializers.CharField(source='comments', allow_blank=True)

    class Meta:
        model = EmployeeDoc
        fields = ('id', 'agency_employee_id', 'doc_type_id', 'start', 'end', 'text')

    def validate(self, data):
        employee = data['agency_employee']
        # Дата начала действия документа не может быть больше даты окончания действия
        start = data.get('start', None)
        end = data.get('end', None)
        if start and end and start > end:
            raise serializers.ValidationError("Дата окончания действия документа меньше даты начала")
        # Проверка специфичных условий для документов вида "Медицинская книжка"
        if data['doc_type'].code == 'medical':
            # - даты начала и окончания действия документа являются обязательными
            if not start:
                raise serializers.ValidationError({"start": "Необходимо заполнить дату начала действия документа"})
            if not end:
                raise serializers.ValidationError({'end': "Необходимо заполнить дату окончания действия документа"})
            # - период действия документа не может быть больше 1 года
            if (end - start).days > 365:
                raise serializers.ValidationError("Срок действия документа не может быть более 1 года")
            # - документ не может заканчиваться более чем через год от текущей даты
            if (end - timezone.now().date()).days > 365:
                raise serializers.ValidationError("Срок действия документа не может быть более 1 года от текущей даты")
        return data

    def update(self, instance, validated_data, current_user):
        # Корректируем значения полей
        for attr_name in ['agency_employee', 'doc_type', 'start', 'end', 'comments']:
            setattr(instance, attr_name, validated_data.get(attr_name, getattr(instance, attr_name)))
        # Сохраняем изменения
        instance.save()
        return instance

    def create(self, validated_data, current_user):
        # Создаем новый объект
        return EmployeeDoc.objects.create(**validated_data)


class GetTransitionAgencyEmployeeSerializer(serializers.Serializer):
    agency_employee_id = serializers.IntegerField()
    def validate_agency_employee_id(self, value):
        try:
            return AgencyEmployee.objects.get(pk=value)
        except AgencyEmployee.DoesNotExist:
            raise serializers.ValidationError("Сотрудник не найден")


class TransitionAgencyEmployeeSerializer(GetTransitionAgencyEmployeeSerializer):
    agency = serializers.IntegerField()
    date_transition = serializers.DateField()

    def validate_agency(self, value):
        try:
            return Agency.objects.get(pk=value)
        except Agency.DoesNotExist:
            raise serializers.ValidationError("Агенство не найдено")

    def validate_date_transition(self, value):
        if datetime.date.today() < value:
            return value
        else:
            raise serializers.ValidationError("Дата должна быть больше текущей")

    def validate(self, attrs):
        # @TODO проверять, разрешено ли перемещение в рамках хеадквотер и находится ли оно в этих рапмках
        #if attrs['agency'].headquater != AgencyEmployee.h
        return super(TransitionAgencyEmployeeSerializer, self).validate(attrs)


class AgencySerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=255, source='name')
    class Meta:
        model = Agency
        fields = ('id', 'text')


class SelectAgencySerializer(serializers.Serializer):
    agencies = AgencySerializer(many=True, read_only=True)
    min_date_transition = serializers.DateField(read_only=True)


class AgencyHistorySerializer(serializers.ModelSerializer):
    agency = serializers.SerializerMethodField('agency_name')

    class Meta:
        model = AgencyHistory
        fields = ('id', 'agency', 'start', 'end')

    def agency_name(self, data):
        return data.agency.name


class AgencyManagerSerializer(serializers.ModelSerializer):
    """Информация об менеджере агентства"""
    class Meta:
        model = AgencyManager
        fields = ("full_name", "position", "phone", "email")
