# common/paginator.py
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import connections, transaction, OperationalError
from django.utils.functional import cached_property


class TimeLimitedPaginator(Paginator):
    """
    Paginator that enforces a timeout on the count operation and uses cache.
    If the count operations times out, an index estimate value is
    returned instead (if there is no cached value).
    """
    @cached_property
    def count(self):
        key = f"easy_log:{hash(self.object_list.query.__str__())}:count"
        cached_value = cache.get(key)

        if cached_value:
            return cached_value

        # We set the timeout in a db transaction to prevent it from
        #  affecting other transactions.

        with transaction.atomic(using='userlogs'), connections['userlogs'].cursor() as cursor:
            cursor.execute("SET LOCAL statement_timeout TO 100;")
            cursor.execute("SELECT reltuples::BIGINT AS estimate FROM pg_class WHERE relname='easy_log';")
            row = cursor.fetchone()
            try:
                count_value = super().count
                cache.set(key, count_value, 3600)
                return count_value
            except OperationalError:
                cache.set(key, row[0], 3600)
                return row[0]
