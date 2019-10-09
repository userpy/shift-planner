from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.generic import RedirectView

class RunMailerView(RedirectView):

    @method_decorator(staff_member_required)
    def get_redirect_url(self, *args, **kwargs):

        call_command('run_notifier')
        messages.add_message(self.request, messages.SUCCESS,
                             mark_safe('Инициализирована генерация и отправка сообщений'))
        return '/admin/notifications/notifyitem/'
