# coding=utf-8;

from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Delete all users sessions'

    def handle(self, *args, **options):
        Session.objects.all().delete()
        print('All sessions are deleted')
