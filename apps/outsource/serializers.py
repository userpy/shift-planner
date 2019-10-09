#
# Copyright 2018 ООО «Верме»
#
# Файл serializers аутсорсинга для django_rest_framework
# Используется для методов апи
# Для работы нужен rest_framework
#

from rest_framework import serializers
from apps.outsource.models import Agency, Organization, Headquater, Job, Quota, StoreArea
from .methods import *
import calendar


class OrganizationSerializer3(serializers.ModelSerializer):
    """Организации для форм приема/увольнения"""
    headquater = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')

    class Meta:
        model = Organization
        fields = ('id', 'name', 'headquater')


class OrganizationSerializer4(serializers.ModelSerializer):
    """Организации для форм претензий"""
    text = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)

    class Meta:
        model = Organization
        fields = ('id', 'text')


class OrganizationSerializer2(serializers.ModelSerializer):
    """Вышестоящие Организации"""
    class Meta:
        model = Organization
        fields = ('name', 'kind')


class OrganizationSerializer(serializers.ModelSerializer):
    """Организации"""
    parent = OrganizationSerializer2(many=False, read_only=True, allow_null=True)

    class Meta:
        model = Organization
        fields = ('id', 'name', 'code', 'parent')


class HeadquaterSerializer(serializers.ModelSerializer):
    """Клиенты"""
    class Meta:
        model = Organization
        fields = ('id', 'name', 'code')


class HeadquaterSelSerializer(serializers.ModelSerializer):
    """Клиенты для селектора (промо)"""
    text = serializers.CharField(source='name')

    class Meta:
        model = Headquater
        fields = ('id', 'text')


class HeadquaterSerializer2(serializers.ModelSerializer):
    """Клиенты для претензий"""
    class Meta:
        model = Headquater
        fields = ('id', 'name', 'prefix')


class CompanySelSerializer(serializers.ModelSerializer):
    """Компании для селектора"""
    text = serializers.CharField(source='name')
    #children = serializers.BooleanField(source='has_children')
    id = serializers.CharField(source='full_id')
    parent = serializers.CharField(default='#')

    class Meta:
        model = Headquater
        fields = ('id', 'text', 'parent', 'party')


class OrganizationSelSerializer(serializers.ModelSerializer):
    """Организации для селектора"""
    text = serializers.CharField(source='name')
    #children = serializers.BooleanField(source='has_children')
    id = serializers.CharField(source='full_id')
    parent = serializers.CharField(source='full_parent_id')

    class Meta:
        model = Organization
        fields = ('id', 'text', 'headquater_id', 'parent')


class AgencySelSerializer(serializers.ModelSerializer):
    """Агентства для селектора"""
    text = serializers.CharField(source='name')
    #children = serializers.BooleanField(source='has_children')
    id = serializers.CharField(source='full_id')
    parent = serializers.CharField(source='full_parent_id')

    class Meta:
        model = Agency
        fields = ('id', 'text', 'headquater_id', 'parent')


class AgencySerializer(serializers.ModelSerializer):
    """Агентства"""
    class Meta:
        model = Agency
        fields = ('id', 'name')


class AgencySerializer2(serializers.ModelSerializer):
    """Агентства для претензий"""
    text = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)

    class Meta:
        model = Agency
        fields = ('id', 'text')


class JobSerializer(serializers.ModelSerializer):
    """Функции сотрудников"""
    # TODO убрать name, оставить id и text
    text = serializers.CharField(source='name')

    class Meta:
        model = Job
        fields = ('id', 'name', 'text')


class StoreAreaSerializer(serializers.ModelSerializer):
    """Зона магазина"""
    class Meta:
        model = StoreArea
        fields = ('id', 'name', 'code')


class StoreAreaSelSerializer(serializers.ModelSerializer):
    """Зона магазина для селектора"""
    text = serializers.CharField(source='name')

    class Meta:
        model = StoreArea
        fields = ('id', 'text')


class QuotaReadSerializer(serializers.ModelSerializer):
    """Квоты чтение"""
    promo = HeadquaterSerializer(many=False, read_only=True)
    store = OrganizationSerializer(many=False, read_only=True)
    area = StoreAreaSerializer(many=False, read_only=True)
    max_value = serializers.CharField(default='-')
    free_value = serializers.CharField(default='-')
    is_active = serializers.BooleanField(default=True)
    shifts_count = serializers.CharField(default='-')
    open_shifts_count = serializers.CharField(default='-')

    class Meta:
        model = Quota
        fields = ('id', 'promo', 'store', 'area', 'quota_type', 'value', 'value_ext', 'max_value', 'free_value',
                  'start', 'end', 'is_active', 'shifts_count', 'open_shifts_count')


class QuotaWriteSerializer(serializers.ModelSerializer):
    """Квоты запись"""
    promo_id = serializers.PrimaryKeyRelatedField(queryset=Headquater.objects.filter(party__in=['promo', 'broker']),
                                                  write_only=True, allow_null=False, source='promo')
    store_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(),
                                                  write_only=True, allow_null=False, source='store')
    area_id = serializers.PrimaryKeyRelatedField(queryset=StoreArea.objects.all(),
                                                 write_only=True, allow_null=False, source='area')

    class Meta:
        model = Quota
        fields = ('id', 'promo_id', 'store_id', 'area_id', 'quota_type', 'value', 'value_ext', 'start', 'end')
        validators = []

    def validate(self, value):
        if 'quota_id' in self.initial_data:
            instance = open_quota(self.initial_data['quota_id'])
        else:
            instance = None
        # Проверка наличия связи магазин-агентство
        orglinks = OrgLink.objects.filter(aheadquarter=value['promo'], organization=value['store'])
        if not orglinks.exists():
            raise serializers.ValidationError("Данное агентство не работает с указанным магазином. "
                                              "Создайте связь в Конфигураторе, затем еще раз попробуйте создать квоту")
        if value['end'] and value['end'] < value['start']:
            raise serializers.ValidationError("Дата окончания квоты не может быть ранее даты начала.")
        # Проверяем, есть ли квота с идентичным набором store, area, promo
        quota = similar_quota(value['store'], value['area'], value['promo'], value['start'])
        if quota and (not instance or instance.id != quota.id):
            raise serializers.ValidationError('Дублирование квот не допускается')
        return value

    def validate_start(self, value):
        if value.day != 1:
            value = value.replace(day=1)
        return value

    def validate_end(self, value):
        if value:
            month_max_day = calendar.monthrange(value.year, value.month)[1]
            if value.day != month_max_day:
                value = value.replace(day=month_max_day)
        return value

    def validate_value(self, value):
        if int(value) < 0:
            raise serializers.ValidationError('Значение квоты должно быть положительным')
        return value

    def validate_value_ext(self, value_ext):
        if int(value_ext) < 0:
            raise serializers.ValidationError('Значение согласованных квот должно быть положительным')
        return value_ext

    def update(self, instance, validated_data, current_user):
        # Новые параметры квоты
        promo = validated_data.get('promo', instance.promo)
        store = validated_data.get('store', instance.store)
        area = validated_data.get('area', instance.area)
        value = validated_data.get('value', instance.value)
        value_ext = validated_data.get('value_ext', instance.value_ext)
        start = validated_data.get('start', instance.start)
        end = validated_data.get('end', instance.end)
        # Если в квоте изменен промоутер, магазин или зона магазина, удаляем все промо смены
        if promo != instance.promo or store != instance.store or area != instance.area or start != instance.start or end != instance.end:
            remove_quota_related_shifts(instance, current_user.id)
            # Сохраняем изменения
            instance.promo = promo
            instance.store = store
            instance.area = area
            instance.value = value
            instance.value_ext = value_ext
            instance.start = start
            instance.end = end
            instance.save()
        # В противном случае запускаем алгоритм изменения значения квоты
        else:
            instance.value = value
            instance.value_ext = value_ext
            instance.start = start
            instance.end = end
            instance.save()

        return instance


class QuotaVolumeReadSerializer(serializers.ModelSerializer):
    """Ограничение квот чтение"""
    store = OrganizationSerializer(many=False, read_only=True)
    area = StoreAreaSerializer(many=False, read_only=True)

    class Meta:
        model = QuotaVolume
        fields = ('id', 'store', 'area', 'kind', 'value', 'start', 'end')


class QuotaVolumeWriteSerializer(serializers.ModelSerializer):
    """Ограничение квот запись"""
    store_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(),
                                                  write_only=True, allow_null=False, source='store')
    area_id = serializers.PrimaryKeyRelatedField(queryset=StoreArea.objects.all(),
                                                 write_only=True, allow_null=False, source='area')

    class Meta:
        model = QuotaVolume
        fields = ('id', 'store_id', 'area_id', 'kind', 'value', 'start', 'end')
        validators = []

    def validate(self, value):
        if 'quota_volume_id' in self.initial_data:
            instance = open_quota_volume(self.initial_data['quota_volume_id'])
        else:
            instance = None
        if value['end'] and value['end'] < value['start']:
            raise serializers.ValidationError("Дата окончания ограничения не может быть ранее даты начала.")
        # Проверяем, есть ли ограничение квот с идентичным набором store, area, start
        quota_volume = active_quota_volume(value['store'], value['area'], value['start'])
        if quota_volume and (not instance or instance.id != quota_volume.id):
            raise serializers.ValidationError('Дублирование ограничения квот не допускается')
        return value

    def validate_value(self, value):
        if int(value) < 0:
            raise serializers.ValidationError('Значение ограничения квот должно быть положительным')
        return value

    def validate_start(self, value):
        if value.day != 1:
            value = value.replace(day=1)
        return value

    def validate_end(self, value):
        if value:
            month_max_day = calendar.monthrange(value.year, value.month)[1]
            if value.day != month_max_day:
                value = value.replace(day=month_max_day)
        return value

    def update(self, instance, validated_data, current_user):
        # Новые параметры ограничения квот
        store = validated_data.get('store', instance.store)
        area = validated_data.get('area', instance.area)
        value = validated_data.get('value', instance.value)
        start = validated_data.get('start', instance.start)
        end = validated_data.get('end', instance.end)
        # Если в ограничении квот изменен магазин или зона магазина или сроки действия,
        # удаляем все квоты связанные с ограничением
        #if store != instance.store or area != instance.area or start != instance.start or end != instance.end:
        #    remove_quota_volume_related_quota(instance)
        #    # Сохраняем изменения
        #    instance.store = store
        #    instance.area = area
        #    instance.value = value
        #    instance.start = start
        #    instance.end = end
        #    instance.save()
        # В противном случае запускаем алгоритм изменения значения ограниения квоты
        #else:
        #    instance.value = value
        #    instance.save()
        # Сохраняем изменения
        instance.store = store
        instance.area = area
        instance.value = value
        instance.start = start
        instance.end = end
        instance.save()

        return instance


class ApiAgencyInfoRequestSerializer(serializers.Serializer):
    """Запрос информации об агентстве"""
    agency_id = serializers.IntegerField(default=0,)
    employee_id =  serializers.IntegerField(default=0,)
    def validate(self, value):
        if not value['agency_id'] and not value['employee_id']:
            serializers.ValidationError('Не введен обячзательный параметр')
        return value


class AgencyInfoSerializer(serializers.ModelSerializer):
    """Информация об агентстве"""
    from apps.employees.serializers import AgencyManagerSerializer
    managers = AgencyManagerSerializer(many=True, read_only=True, source='agencymanager_set')

    class Meta:
        model = Agency
        fields = ("name", "code", "full_name", "address", "actual_address", "phone", "site", "email", "description", "managers")