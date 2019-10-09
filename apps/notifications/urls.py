from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^admin/run-mailer/$', views.RunMailerView.as_view(), name='admin-run-mailer'),
    url(r'^notify_employees_schedule/$', views.NotifyEmployeesScheduleView.as_view(), name='notify-employees-schedule'),
]
