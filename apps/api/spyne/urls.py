#
# Copyright 2018 ООО «Верме»
#
# Файл описания URL сервисов Spyne
#

from django.conf.urls import url

from .services import outsourcing_soap_service, outsourcing_rest_service


urlpatterns = [
    url(r'soap/$', outsourcing_soap_service),
    url(r'rest/$', outsourcing_rest_service),
]