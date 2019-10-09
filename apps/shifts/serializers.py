#
# Copyright 2018 ООО «Верме»
#
# Файл serializers заявок и смен для django_rest_framework
# Используется для методов апи
# Для работы нужен rest_framework
#

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from rest_framework import serializers
from .models import *
from .methods import *
from apps.employees.models import AgencyEmployee
from apps.employees.serializers import AgencyEmployeeSerializer, AgencyEmployeeListSerializer
from apps.outsource.models import Agency, Organization, Job, StoreArea, Quota
from apps.outsource.methods import active_quota
from apps.shifts.methods import check_availability
from apps.outsource.serializers import OrganizationSerializer, AgencySerializer
import calendar


class ShiftWorkloadSerializer(serializers.ModelSerializer):
    """Смены с указанием количества смен в состоянии accept
    и наименованием функций на дату начала смены"""
    workload = serializers.ListField(read_only=True)

    class Meta:
        model = OutsourcingShift
        fields = ('start_date', 'workload')


class OutsourcingRequestSerializer(serializers.ModelSerializer):
    """Запрос сотрудников"""
    organization = OrganizationSerializer(many=False, read_only=True, allow_null=False)

    class Meta:
        model = OutsourcingRequest
        fields = ('id', 'guid', 'organization')


class OutsourcingRequestExtSerializer(serializers.ModelSerializer):
    """Список заявок на аутсорcинг"""
    organization = OrganizationSerializer(many=False, read_only=True)
    agency = AgencySerializer(many=False, read_only=True)
    dt_accepted = serializers.DateTimeField(read_only=True)
    shifts_count = serializers.IntegerField(source='get_request_shifts_count')
    duration = serializers.IntegerField(source='get_request_shifts_duration')
    jobs = serializers.ListField(source='get_request_shifts_jobs')

    class Meta:
        model = OutsourcingRequest
        fields = ('id', 'organization', 'agency', 'start', 'end', 'dt_accepted', 'state',
                  'shifts_count', 'duration', 'jobs')


class OusourcingShiftSerializer(serializers.ModelSerializer):
    """ Смены сотрудников аутсорсинговых агентств """
    job = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    agency_employee = AgencyEmployeeSerializer(many=False, read_only=True, allow_null=True)
    agency_employee_id = serializers.PrimaryKeyRelatedField(queryset=AgencyEmployee.objects.all(),
                                                            source='agency_employee', write_only=True)
    agency = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    request = OutsourcingRequestSerializer(many=False, read_only=True)
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = OutsourcingShift
        fields = ('id', 'start', 'end', 'job', 'agency_employee', 'agency_employee_id', 'agency', 'request')


class OusourcingShiftSerializer2(serializers.ModelSerializer):
    """Назначение сотрудника на смену"""
    agency_employee_id = serializers.PrimaryKeyRelatedField(queryset=AgencyEmployee.objects.all(),
                                                            source='agency_employee', write_only=True, allow_null=True)

    class Meta:
        model = OutsourcingShift
        fields = ('id', 'agency_employee_id')


class OutsourcingShiftReadSerializer(serializers.ModelSerializer):
    """ Смены аутсорсеров (чтение) """
    agency_id = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all(), source='agency')
    organization_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(),
                                                         source='get_organization_id')
    employee_id = serializers.PrimaryKeyRelatedField(queryset=AgencyEmployee.objects.all(), source='agency_employee',
                                                     allow_null=True, required=False)
    employee = AgencyEmployeeListSerializer(source='agency_employee', many=False, allow_null=True, required=False)
    urow_index = serializers.IntegerField(default=0)
    area_id = serializers.CharField(source='get_area_id')
    worktime = serializers.IntegerField(source='get_duration')

    class Meta:
        model = OutsourcingShift
        fields = (
            'id', 'start', 'end', 'state', 'agency_id', 'organization_id', 'employee_id', 'employee', 'area_id',
            'worktime',
            'urow_index')
        read_only_fields = (
            'id', 'start', 'end', 'state', 'agency_id', 'organization_id', 'employee_id', 'employee', 'area_id',
            'worktime',
            'urow_index')


def date_validator(input_date):
    if not input_date:
        return None
    else:
        try:
            return datetime.datetime.strptime(input_date, '%Y-%m-%d').date()
        except:
            raise serializers.ValidationError('Неправильный формат даты')


def orgtype_validator(input_date):
    if input_date:
        orgtype_array = input_date.split('_')
        if len(orgtype_array) == 2 and orgtype_array[1] in ['headquater', 'agency', 'organization']:
            try:
                orgtype_array[0] = int(orgtype_array[0])
                return orgtype_array
            except Exception:
                pass
    raise serializers.ValidationError('Неправильный формат orgtype')


class ApiClientScheduleRequestSerializer(serializers.Serializer):
    start = serializers.CharField(max_length=10, validators=[date_validator, ])
    end = serializers.CharField(max_length=10, validators=[date_validator, ])
    month = serializers.CharField(max_length=10, validators=[date_validator, ], allow_blank=True, default=None)
    orgunit = serializers.CharField(max_length=255, validators=[orgtype_validator, ])
    export = serializers.CharField(max_length=255, allow_blank=True, default=None)
    party = serializers.CharField(max_length=255, allow_blank=True, default='client')
    def validate_orgunit(self, input_date):
        if input_date:
            orgtype_array = input_date.split('_')
            if len(orgtype_array) == 2 and orgtype_array[1] in ['headquater', 'agency', 'organization']:
                try:
                    orgtype_array[0] = int(orgtype_array[0])
                    return orgtype_array
                except Exception:
                    pass
        raise serializers.ValidationError('Неправильный формат orgtype')

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name')

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreArea
        fields = ('id', 'name', 'color', 'icon', )

class QuotaSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(source='store')
    area = AreaSerializer()
    #size = serializers.SerializerMethodField()
    size = serializers.IntegerField(source='value_total')
    def get_size(self, obj):
        return obj.value_total
    class Meta:
        model = Quota
        fields = ('organization', 'area', 'size')

class PromoShiftReadSerializer(serializers.ModelSerializer):
    """ Смены промоутеров (чтение) """
    area_id = serializers.PrimaryKeyRelatedField(queryset=StoreArea.objects.all(), source='store_area')
    agency_id = serializers.CharField(source='agency_city')
    #agency_id = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all(), source='agency')
    organization_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), source='organization')
    employee_id = serializers.PrimaryKeyRelatedField(queryset=AgencyEmployee.objects.all(), source='agency_employee',
                                                     allow_null=True, required=False)
    employee = AgencyEmployeeListSerializer(source='agency_employee', many=False, allow_null=True, required=False)
    urow_index = serializers.IntegerField(source='quota_number')
    has_violations = serializers.BooleanField(default=False)

    class Meta:
        model = PromoShift
        fields = (
            'id', 'start', 'end', 'state', 'area_id', 'agency_id', 'organization_id', 'employee_id', 'employee',
            'duration',
            'worktime', 'urow_index', 'has_violations')
        read_only_fields = (
            'id', 'start', 'end', 'state', 'area_id', 'agency_id', 'organization_id', 'employee_id', 'employee',
            'duration',
            'worktime', 'urow_index', 'has_violations')


class PromoShiftReturnSerializer(serializers.Serializer):
    shift = PromoShiftReadSerializer(many=False, read_only=True)


class AvailabilityReadSerializer(serializers.ModelSerializer):
    """ Доступности (чтение) """
    area_id = serializers.PrimaryKeyRelatedField(queryset=StoreArea.objects.all(), source='store_area')
    agency_id = serializers.CharField(source='agency_city')
    #agency_id = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all(), source='agency')
    organization_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), source='organization')

    class Meta:
        model = Availability
        fields = ('id', 'start', 'end', 'area_id', 'agency_id', 'organization_id', 'kind')
        read_only_fields = ('id', 'start', 'end', 'area_id', 'agency_id', 'organization_id')


class AvailabilityWriteSerializer(serializers.ModelSerializer):
    """ Доступности (запись) """
    id = serializers.IntegerField(min_value=1, required=False)
    area_id = serializers.PrimaryKeyRelatedField(queryset=StoreArea.objects.all(), source='store_area', required=True)
    agency_id = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all(), source='agency', required=True)
    organization_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), source='organization',
                                                         required=True)

    class Meta:
        model = Availability
        fields = ('id', 'start', 'end', 'area_id', 'agency_id', 'organization_id', 'kind')

    @staticmethod
    def set_dtime_15m(value):
        value.replace(second=0)
        value.replace(microsecond=0)
        modulo = value.minute % 15
        if modulo != 0:
            value.replace(minute=value.minute - modulo)
        return value

    def validate(self, data):
        # Определение пересечения интервалов доступности
        avail_id = [data.get('id')] if data.get('id') else []
        avail_exists = check_availability(data['organization'], data['store_area'], data['agency'], data['start'], data['end'], data['kind'], avail_id)
        if avail_exists:
            raise serializers.ValidationError("Данный интервал пересекается с другой доступностью")
        # TODO silent режим
        #self.check_availability(avail, data)
        # Корректируем начало - конец, если они не кратны 15 минутам до ближайшей 15-минутки вниз
        # data['start'] = self.set_dtime_15m(data['start'])
        # data['end'] = self.set_dtime_15m(data['end'])
        return data

    def find_instance(self, validated_data, overwrite):
        """Вспомогательный метод - определение редактируемого объекта"""
        # Доступность может быть задана явно через идентификатор
        instance = open_availability(validated_data.get('id'))
        # Если разрешено перезаписывать существующие доступности, то удаляем те доступности, которые накрывается создаваемой
        if not instance and overwrite:
            Availability.find_overlay(
                validated_data['agency'],
                validated_data['organization'],
                validated_data['store_area'],
                validated_data['start'],
                validated_data['end']
            ).delete()
            return None
        # Возвращаем найденный объект
        return instance

    def check_availability(self, instance, validated_data):
        """Вспомогательный метод, проверка soft-ограничений"""
        # Проверяем, что смена не выходит за допустимый предел
        start = validated_data['start']
        today = datetime.datetime.today().date()
        if start < today:
            return "Настройками системы не допускается изменение графика доступностей задним числом"
        max_date = today + relativedelta(months=2)
        max_date = max_date.replace(day=calendar.monthrange(max_date.year, max_date.month)[1])
        if start > max_date:
            return "Настройками системы ограничена возможность создания доступностей дальше, чем на 2 месяца в будущее"
        # Выходим в случае обнаружения пересечения смен
        agency = validated_data['agency']
        organization = validated_data['organization']
        end = validated_data['end']
        store_area = validated_data['store_area']
        avail_ids = [instance.id] if instance else []
        if Availability.find_overlay(agency, organization, store_area, start, end, avail_ids).exists():
            return "Сохранение невозможно, т.к. обнаружено пересечение доступностей"
        if Availability.find_shifts(agency, organization, store_area, start, end).exists():
            return "Сохранение невозможно, т.к. в интервале доступности существуют смены"

    def update(self, instance, validated_data, current_user):
        # Изменение агентства допускается только на уровне одной компании
        agency = validated_data.get('agency', instance.agency)
        if (agency.headquater == instance.aheadquarter):
            instance.agency = agency
        # Изменение магазина допускается также только на уровне клиента
        organization = validated_data.get('organization', instance.organization)
        if (organization.headquater == instance.organization):
            instance.organization = organization
        # Корректируем значения полей
        for attr_name in ['store_area', 'start', 'end']:
            setattr(instance, attr_name, validated_data.get(attr_name, getattr(instance, attr_name)))
        # Сохраняем изменения
        instance.save()
        return instance


class AvailabilityReturnSerializer(serializers.Serializer):
    avail = AvailabilityReadSerializer(many=False, read_only=True)


''' ***************************************** СМЕНЫ ПРОМОУТЕРОВ ********************************************* '''


class PromoShiftWriteSerializer(serializers.ModelSerializer):
    """ Смены промоутеров (запись) """
    area_id = serializers.PrimaryKeyRelatedField(queryset=StoreArea.objects.all(), source='store_area', required=True)
    agency_id = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all(), source='agency', required=True)
    organization_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), source='organization',
                                                         required=True)
    employee_id = serializers.PrimaryKeyRelatedField(queryset=AgencyEmployee.objects.all(), source='agency_employee',
                                                     required=False, allow_null=True)
    urow_index = serializers.IntegerField(source='quota_number', required=True)

    class Meta:
        model = PromoShift
        fields = ('id', 'start', 'end', 'area_id', 'agency_id', 'organization_id', 'employee_id', 'urow_index')

    @staticmethod
    def set_dtime_15m(value):
        value.replace(second=0)
        value.replace(microsecond=0)
        modulo = value.minute % 15
        if modulo != 0:
            value.replace(minute=value.minute - modulo)
        return value

    def validate(self, data):
        # Определение интервалов доступности
        avail = check_availability(data['organization'], data['store_area'], data['agency'], data['start'], data['end'], 0)
        if avail:
            raise serializers.ValidationError("Данный интервал недоступен для смены")
        # Минимальная продолжительность смены должна быть не менее 4-х часов и не блоее 13 часов
        shift_duration = (data['end'] - data['start']).total_seconds()
        if shift_duration < 14400:
            raise serializers.ValidationError("Продолжительность смены должна быть не меньше 4-х часов")
        if shift_duration > 46800:
            raise serializers.ValidationError("Продолжительность смены должна быть не более 13-ти часов")
        # TODO - Убрать в дальнейшем
        if (data['end'] - timedelta(seconds=900)).date() != data['start'].date():
            raise serializers.ValidationError("Создание переходящих смен запрещено настройками системы.")
        # Определяем, соответствуют ли переданные параметры назначенным квотам
        quota = active_quota(data['organization'], data['store_area'], data['agency'].headquater, data['start'].date())
        if not quota:
            raise serializers.ValidationError("У агентства нет активной квоты на выбранный магазин")
        if int(data['quota_number']) >= quota.value_total:
            raise serializers.ValidationError("Указанный номер квоты превышает число доступных квот агентству")
        # Проверям, можем ли быть назначен выбранный сотрудник на смену
        if data.get('agency_employee', None):
            if data['agency'] != data['agency_employee'].agency:
                raise serializers.ValidationError("Выбранный сотрудник не работает в выбранном агентстве")
        # Корректируем начало - конец, если они не кратны 15 минутам до ближайшей 15-минутки вниз
        data['start'] = self.set_dtime_15m(data['start'])
        data['end'] = self.set_dtime_15m(data['end'])
        return data

    def find_instance(self, validated_data, overwrite):
        """Вспомогательный метод - определение редактируемого объекта"""
        # Смена может быть задана явно через идентификатор
        instance = open_promo_shift(validated_data.get('id'))
        # Если разрешено перезаписывать существующие смены, то редактируем ту смену, которая накрывается создаваемой
        if not instance and overwrite:
            instance = PromoShift.find_overlay(
                validated_data['agency'],
                validated_data['organization'],
                validated_data['store_area'],
                validated_data['quota_number'],
                validated_data['start'],
                validated_data['end']
            ).first()
        # Возвращаем найденный объект
        return instance

    def check_shift(self, instance, validated_data):
        """Вспомогательный метод, проверка soft-ограничений"""
        # Проверяем, что смена не выходит за допустимый предел
        start = validated_data['start']
        today = datetime.datetime.today().date()
        if start.date() < today:
            return serializers.ValidationError(
                "Настройками системы не допускается изменение графика смен задним числом")
        max_date = today + relativedelta(months=2)
        max_date = max_date.replace(day=calendar.monthrange(max_date.year, max_date.month)[1])
        if start.date() > max_date:
            return serializers.ValidationError(
                "Настройками системы ограничена возможность создания смен дальше, чем на 2 месяца в будущее")
        # Выходим в случае обнаружения пересечения смен
        agency = validated_data['agency']
        organization = validated_data['organization']
        end = validated_data['end']
        store_area = validated_data['store_area']
        quota_number = validated_data['quota_number']
        shift_ids = [instance.id] if instance else []
        if PromoShift.find_overlay(agency, organization, store_area, quota_number, start, end, shift_ids).exists():
            return serializers.ValidationError("Сохранение невозможно, т.к. обнаружено пересечение смен")
        # Определяем, соответствуют ли переданные параметры назначенным квотам
        quota = active_quota(organization, store_area, agency.headquater, start.date())
        if quota_number >= quota.value_total:
            return serializers.ValidationError("Указанный номер квоты превышает число доступных квот агентству")

    def update(self, instance, validated_data, current_user):
        # Изменение агентства допускается только на уровне одной компании
        agency = validated_data.get('agency', instance.agency)
        if (agency.headquater == instance.aheadquarter):
            instance.agency = agency
        # Изменение магазина допускается также только на уровне клиента
        organization = validated_data.get('organization', instance.organization)
        if (organization.headquater == instance.organization):
            instance.organization = organization
        # Корректируем значения полей
        for attr_name in ['store_area', 'quota_number', 'start', 'end']:
            setattr(instance, attr_name, validated_data.get(attr_name, getattr(instance, attr_name)))
        # Проверяем, можно ли назначить сотрудника на выбранный день
        agency_employee = validated_data.get('agency_employee', None)
        if agency_employee and not can_set_employee_to_shft(agency_employee, instance):
            agency_employee = None
        instance.agency_employee = agency_employee
        # Сохраняем изменения
        instance.save()
        return instance

    def create(self, validated_data, current_user):
        # Определяем, может ли сотрудник замещать смену
        agency = validated_data['agency']
        organization = validated_data['organization']
        agency_employee = validated_data.get('agency_employee', None)
        start = validated_data['start']
        end = validated_data['end']
        if agency_employee and not can_set_employee_to_shft_ext(agency_employee, start, end, agency,
                                                                organization.headquater, None):
            agency_employee = None
        # Создаем новый объект
        return PromoShift.objects.create(agency=agency, organization=organization,
                                         store_area=validated_data['store_area'],
                                         quota_number=validated_data['quota_number'], start=start, end=end,
                                         agency_employee=agency_employee)

import json
class ApiExportEmployeeShiftsRequestSerializer(serializers.Serializer):
    start = serializers.CharField(max_length=10, validators=[date_validator, ])
    end = serializers.CharField(max_length=10, validators=[date_validator, ])
    employee_list = serializers.ListField(default=[])
    def validate_employee_list(self, employee_list):
        if len(employee_list) < 0:
            raise serializers.ValidationError('Не может быть пустым')
        elif employee_list[0][0] == '[':
            try:
                employee_list = json.loads(employee_list[0])
            except:
                raise serializers.ValidationError('Неправильный формат данных')
        return employee_list
