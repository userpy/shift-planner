from datetime import datetime, date


class DiffMixin(object):
    """
    Класс для вычисления изменений в обектах при сохранении (в основном для логов).
    Пример:
        class Post(DiffMixin, Model):
            user = ForeignKey(User)
            text = TextField()
            created_at = DateTimeField()
            diff_fields = ['user_id', 'text']

        post = Post.objects.get(pk=123)
        post.capture_diff_data()
        form = PostForm(request.POST, instance=post)
        diff = post.get_diff()

        # если все поля изменились:
        diff == {
            'user_id': {'from': 1 'to': 2},
            'text': {'from': 'before', 'to': 'after'}
        }
        # если user не изменился:
        diff == {
            'text': {'from': 'before', 'to': 'after'}
        }
    """
    _diff_data = {}

    # @classmethod
    # def check(cls, **kwargs):
    #     errors = super().check(**kwargs)
    #     # check diff_fields
    #     return errors

    def convert_diff_value(self, val):
        """ Конвертирует значение в то, что можно легко сравнить и сохранить. """
        if isinstance(val, datetime) or isinstance(val, date):
            return val.isoformat()
        else:
            return val

    def get_diff_value(self, field_name):
        """ Возвращает значение атрибута, конвертиурет его. """
        return self.convert_diff_value(getattr(self, field_name))

    def capture_diff_data(self):
        """ Собирет значения из diff_fields, результат сохраняет в объекте и возвращает. """
        self._diff_data.clear()
        for field_name in self.diff_fields:
            self._diff_data[field_name] = self.get_diff_value(field_name)
        return self._diff_data

    def get_diff(self, diff_data=None):
        """ Вычисляет разницу после изменения каких-либо полей.
            До изменений должен был быть вызван capture_diff_data на этом объекте.
            Либо на другом, а результат передан в параметр diff_data.
            Возвращает изменения в виде: {'field': {'from': 'before', 'to': 'after}, ...} """
        if diff_data is None:
            diff_data = self._diff_data

        diff = {}
        for field_name in self.diff_fields:
            if field_name in diff_data:
                old_value = diff_data[field_name]
                new_value = self.get_diff_value(field_name)
                if new_value != old_value:
                    diff[field_name] = {'from': old_value, 'to': new_value}
        return diff
