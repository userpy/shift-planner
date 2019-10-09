# coding=utf-8;

from django.core.management.base import BaseCommand

from apps.notifications.notify_item_processor import NotifyItemProcessor


class Command(BaseCommand):

    def handle(self, *args, **options):
        processor = NotifyItemProcessor()
        processor.process()
