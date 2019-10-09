from django.db.models.aggregates import Aggregate


class ArrayAgg(Aggregate):
    function = 'array_agg'
