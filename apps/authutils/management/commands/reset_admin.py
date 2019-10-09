# coding=utf-8;

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):

    help = "Set admin user as staff and set password to `123`"

    def handle(self, *args, **options):
        u = User.objects.get(username='admin')
        u.is_staff = True
        u.set_password('123')
        u.save()