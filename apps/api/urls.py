#
# Copyright 2018 ООО «Верме»
#
# Файл описания URL Spyne
#

from django.conf.urls import url, include


urlpatterns = [
    url(r'^', include('apps.api.spyne.urls')),
]