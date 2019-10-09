def renamed(attr, name):
    """ Возвращает переименованное поле для админского list_display.
        Пример:
    class SmthAdmin(admin.ModelAdmin):
        value = renamed('value', 'значеие')
        list_display = ('name', value) """
    def func(obj):
        return getattr(obj, attr)
    func.short_description = name
    return func
