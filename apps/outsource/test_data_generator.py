import factory
from django.utils import timezone

from apps.outsource.models import Headquater, Organization, Agency, Job
from apps.shifts.models import OutsourcingRequest, OutsourcingShift


# Генератор функций
class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job
    name = factory.Sequence(lambda n: 'Job {}'.format(n))
    code = factory.Sequence(lambda n: 'job_{}'.format(n))


# Генератор клиентов
class HeadquaterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Headquater
    name = factory.Sequence(lambda n: 'Headquater {}'.format(n))
    code = factory.Sequence(lambda n: 'head_{}'.format(n))


# Генератор организаций
class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization
    name = factory.Sequence(lambda n: 'Organization {}'.format(n))
    code = factory.Sequence(lambda n: 'org_{}'.format(n))
    headquater = factory.SubFactory(HeadquaterFactory)
    kind = 'city'


# Генератор агентств
class AgencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Agency
    name = factory.Sequence(lambda n: 'Agency {}'.format(n))
    code = factory.Sequence(lambda n: 'agency_{}'.format(n))


# Генератор запросов
class OutsourcingRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OutsourcingRequest
    headquater_id = factory.LazyAttribute(lambda o: '%s' % o.organization.headquater.id)
    agency = factory.SubFactory(AgencyFactory)
    organization = factory.SubFactory(OrganizationFactory)
    state = 'accepted'
    start = timezone.now().date()
    end = timezone.now().date()


# Генератор смен
class OutsourcingShiftFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OutsourcingShift
    state = 'wait'
    start = timezone.now()
    end = timezone.now()
    worktime = '60'
    job = factory.SubFactory(JobFactory)
    request = factory.Sequence(lambda n: '{}'.format(n))
    headquater_id = factory.Sequence(lambda n: '{}'.format(n))
    agency_id = factory.Sequence(lambda n: '{}'.format(n))
    start_date = timezone.now().date()
