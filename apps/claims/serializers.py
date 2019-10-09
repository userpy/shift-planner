#
# Copyright 2018 ООО «Верме»
#
# Файл serializers претензий для django_rest_framework
# Используется для методов апи
# Для работы нужен rest_framework
#

from django.utils import timezone
from rest_framework import serializers
from apps.outsource.models import Agency, Organization, Config
from apps.claims.models import ClaimStatus, ClaimType, ClaimRequest, ClaimMessage, ClaimAttach, Document
from apps.outsource.serializers import HeadquaterSerializer2, OrganizationSerializer, AgencySerializer


class CustomDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        tz = timezone.get_default_timezone()
        value = timezone.localtime(value, timezone=tz)
        return super().to_representation(value)


class ClaimTypeSerializer(serializers.ModelSerializer):
    """Типы претензий"""
    class Meta:
        model = ClaimType
        fields = ('id', 'name')


class ClaimTypeSerializer2(serializers.ModelSerializer):
    """Типы претензий"""
    text = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)

    class Meta:
        model = ClaimType
        fields = ('id', 'text')


class ClaimStatusSerializer(serializers.ModelSerializer):
    """Статус претензий"""
    class Meta:
        model = ClaimType
        fields = ('id', 'name', 'code')


class ClaimAttachSerializer(serializers.ModelSerializer):
    """Файлы"""
    dt_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ClaimAttach
        fields = ('filename', 'attachment', 'message_id', 'dt_created')


class ClaimSerializer(serializers.ModelSerializer):
    """Претензии"""
    guid = serializers.UUIDField(write_only=True)
    headquater = HeadquaterSerializer2(many=False, read_only=True)
    organization = OrganizationSerializer(many=False, read_only=True)
    agency = AgencySerializer(many=False, read_only=True)
    claim_type = ClaimTypeSerializer(many=False, read_only=True)
    status = ClaimStatusSerializer(many=False, read_only=True)

    organization_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(),
                                                         source='organization', write_only=True, allow_null=False)
    agency_id = serializers.PrimaryKeyRelatedField(queryset=Agency.objects.all(),
                                                   source='agency', write_only=True, allow_null=False)
    claim_type_id = serializers.PrimaryKeyRelatedField(queryset=ClaimType.objects.all(),
                                                       source='claim_type', write_only=True, allow_null=False)
    status_id = serializers.PrimaryKeyRelatedField(queryset=ClaimStatus.objects.all(),
                                                   source='status', write_only=True, allow_null=False, required=False)
    number = serializers.CharField(read_only=True)
    attachments = ClaimAttachSerializer(many=True, read_only=True)
    dt_updated = serializers.DateTimeField(read_only=True)
    dt_created = serializers.DateTimeField(read_only=True)
    dt_status_changed = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ClaimRequest
        fields = ('guid', 'id', 'headquater', 'organization', 'agency', 'number', 'claim_type', 'status', 'text',
                  'dt_created', 'dt_status_changed', 'organization_id', 'agency_id', 'claim_type_id', 'attachments',
                  'dt_updated', 'user_name', 'status_id')


class ClaimMessageSerializer(serializers.ModelSerializer):
    """Сообщения"""
    attachments = ClaimAttachSerializer(many=True, read_only=True)
    claim = serializers.SlugRelatedField(many=False, read_only=True, slug_field='id')
    claim_id = serializers.PrimaryKeyRelatedField(queryset=ClaimRequest.objects.all(),
                                                  source='claim', write_only=True, allow_null=False)
    dt_created = serializers.DateTimeField(read_only=True)
    party_detail = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = ClaimMessage
        fields = ('id', 'claim', 'claim_id', 'party', 'party_detail', 'text', 'user_name', 'dt_created', 'attachments')


class ClaimHistorySerializer(serializers.ModelSerializer):
    """История"""
    claim = serializers.SlugRelatedField(many=False, read_only=True, slug_field='id')
    dt_created = serializers.DateTimeField(read_only=True)
    party_detail = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = ClaimMessage
        fields = ('id', 'claim', 'party', 'party_detail', 'text', 'user_name', 'dt_created')


class ClaimMessageSerializer2(serializers.ModelSerializer):
    """Сообщения для файлов"""
    class Meta:
        model = ClaimMessage
        fields = ('id', 'party', 'user_name')


class ClaimSerializer2(serializers.ModelSerializer):
    """Претензия для файлов"""

    class Meta:
        model = ClaimRequest
        fields = ('id', 'user_name')


class ClaimAttachSerializer2(serializers.ModelSerializer):
    """Файлы для претензии"""
    dt_created = serializers.DateTimeField(read_only=True)
    message = ClaimMessageSerializer2(many=False, read_only=True)
    claim = ClaimSerializer2(many=False, read_only=True)

    class Meta:
        model = ClaimAttach
        fields = ('filename', 'attachment', 'message', 'claim', 'dt_created')


class Base64FileField(serializers.FileField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.
    """
    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        from django.core.files.uploadedfile import UploadedFile
        import base64
        import uuid
        # Support for base64 uploads
        if isinstance(data, str):
            try:
                decoded = base64.b64decode(data)
            except TypeError:
                self.fail("invalid_file")
            data = ContentFile(decoded, name=str(uuid.uuid4()))
        elif isinstance(data, UploadedFile):
            data.name = '{name}.{ext}'.format(name=str(uuid.uuid4()), ext=data.name.split('.')[-1])
        return super(Base64FileField, self).to_internal_value(data)


class AttachmentUploadSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)
    file = Base64FileField(write_only=True)

    claim_id = serializers.PrimaryKeyRelatedField(queryset=ClaimRequest.objects.all(),
                                                  source='claim', write_only=True, required=False)
    message_id = serializers.PrimaryKeyRelatedField(queryset=ClaimMessage.objects.all(),
                                                    source='message', write_only=True, required=False)

    def validate_file(self, value):
        # Определение максимального размера загружаемого файла
        if 'claim_id' in self.initial_data:
            claim = ClaimRequest.objects.filter(id=self.initial_data['claim_id']).first()
        if 'message_id' in self.initial_data:
            message = ClaimMessage.objects.filter(id=self.initial_data['message_id']).first()
            claim = message.claim
        max_filesize_config = Config.objects.filter(headquater=claim.headquater, key='max_file_size').first()

        # Если параметр задан, то используется он, иначе значение по умолчанию
        if not max_filesize_config:
            max_filesize = '1'
        else:
            max_filesize = max_filesize_config.value
        if value.size == 0:
            raise serializers.ValidationError("Empty file")
        if value.size >= int(max_filesize)*1000*1000:
            raise serializers.ValidationError("File size is too big")
        self._file = value
        return value

    def update(self, instance, validated_data):
        instance.save()
        return instance

    def create(self, validated_data):
        """
        Creates ClaimAttach model based on file
        :param validated_data: dict
        :return:
        """
        from django.core.files.uploadedfile import UploadedFile
        import mimetypes
        mimetypes.init()
        file = self._file  # type: UploadedFile
        validated_data['attachment'] = file
        del validated_data['file']
        validated_data['attachment'].name = validated_data['filename']
        validated_data['mime'] = mimetypes.guess_type(validated_data['filename'])[0]
        validated_data['size'] = file.size
        return ClaimAttach.objects.create(**validated_data)


class DocumentSerializer(serializers.ModelSerializer):
    """Документы"""
    dt_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Document
        fields = ('filename', 'attachment', 'description', 'dt_created')
