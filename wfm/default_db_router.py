# coding=utf-8;


class DefaultDBRouter():

    IGNORED_APPS = ('applogs', 'easy_log')

    def is_ignored_app(self, obj):
        return obj._meta.app_label in self.IGNORED_APPS

    def db_for_read(self, model, **hints):
        if self.is_ignored_app(model):
            return None
        return 'default'

    def db_for_write(self, model, **hints):
        if self.is_ignored_app(model):
            return None
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if self.is_ignored_app(obj1) or self.is_ignored_app(obj2):
            return None
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Важен порядок следования роутеров в settings
        # При миграциях, они пойдут через первый роутер, в любом случае,
        # даже если указываем приложение у которого есть свой роутер
        # и базу с ключом --database с именем базы отличным от default
        # оно попадет сюда, при этом "return None" который в документации указан
        # как "router has no option" не вызывает запроса allow_migrate
        # у следующего роутера из списка, что может показаться ожидаемым
        # и проверка данного вида не сработает:

        # if app_label in self.IGNORED_APPS:
        #    return None
        # return True

        # Поэтому проверяем здесь 3 варианта
        # и при обновлении выполняем migrate и migrate applogs --database applogs

        # Приложение, которое должно быть в отдельной базе (в игнор списке)
        # и пытаемся мигрировать его в дефолтную базу, а не отдельную
        # это случай manage.py migrate, который мигрирует все прилоежния
        if app_label in self.IGNORED_APPS and db == 'default':
            # говорим что сюда писать нельзя, несмотря на то что при миграции будет ОК и
            # в django_migrations записи появятся, якобы смигрировали
            # фактически миграция пропущена, и изменений в БД не будет
            # т.к. django не умеет сообщать была ли миграция фактически применена или нет
            return False

        # Приложение, которое должно быть в отдельной базе (в игнор списке)
        # и пытаемся мигрировать его в свою базу, а не дефолтную
        # это случай manage.py migrate applogs --database applogs
        if app_label in self.IGNORED_APPS and db != 'default':
            # приложение в игнор списке, база отличная от дефолтной
            # поэтому все ок, мигрирацию делать можно
            return True

        # Случай, когда выполняем manage.py migrate --database applogs
        # Для приложений не в игнор листе
        # По факту это бы привело к созданию всех таблиц какие были в дефолтной базе
        # для всех приложений в новой базе, аналогично первому случаю
        if db != 'default':
            # говорим что сюда писать нельзя, несмотря на то что при миграции будет ОК и
            # в django_migrations записи появятся, якобы смигрировали
            # фактически миграция пропущена, и изменений в БД не будет
            # т.к. django не умеет сообщать была ли миграция фактически применена или нет
            return False

        # А все остальное можно
        return True
