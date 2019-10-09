#
# Copyright 2018 ООО «Верме»
#
# Файл описания ошибок Spyne
#

from spyne.model.fault import Fault


class AuthenticationError(Fault):
    __namespace__ = 'https://outsourcing-test.verme.ru/api/soap'

    def __init__(self, user_name):
        # TODO: self.transport.http.resp_code = HTTP_401

        super(AuthenticationError, self).__init__(
            faultcode='Client.AuthenticationError',
            faultstring='Invalid authentication request for %r' % user_name
        )


class AuthorizationError(Fault):
    __namespace__ = 'https://outsourcing-test.verme.ru/api/soap'

    def __init__(self):
        # TODO: self.transport.http.resp_code = HTTP_401

        super(AuthorizationError, self).__init__(
            faultcode='Client.AuthorizationError',
            faultstring='You are not authozied to access this resource.'
        )

class CustomError(Fault):
    __namespace__ = 'https://outsourcing-test.verme.ru/api/soap'

    def __init__(self, message):
        # TODO: self.transport.http.resp_code = HTTP_401

        super(CustomError, self).__init__(
            faultcode='Custom.Error',
            faultstring=message
        )