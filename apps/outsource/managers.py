from django.db.models import Manager, Q


class QuotaManager(Manager):

    def date_filter(self, start, end):
        """
        Выборка активных квот по датам и сортировка
        :param start:
        :param end:
        :return:
        """
        return self.filter(Q(start__lte=start, end__isnull=True) | Q(start__lte=start, end__gte=end))
