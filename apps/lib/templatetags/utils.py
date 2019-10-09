import json
import os

from django.conf import settings
from django.template import Library
from django.utils.html import format_html
from glob import glob

register = Library()


@register.filter
def jsonify(obj):
    # if isinstance(object, ValuesListQuerySet):
    #     return mark_safe(json.dumps(list(object)))
    # if isinstance(obj, QuerySet):
    #     return mark_safe(serialize('json', obj))
    return json.dumps(obj, ensure_ascii=False)  # .encode('utf8')


@register.filter(name='not')
def not_filter(value):
    return not value


@register.filter
def class_name(obj):
    return obj.__class__.__name__


@register.filter
def repeat(string, times):
    return string * times


def find_files(filepath, ordered_names):
    files = []
    for root in settings.STATICFILES_DIRS:  # находим все файлы
        if not root.endswith('/'):
            root += '/'
        files.extend(settings.STATIC_URL + fpath[len(root):]
                     for fpath in sorted(glob(root + filepath, recursive=True))
                     if fpath.startswith(root))

    if len(files) == 0:  # если их нет, с путём что-то не так
        raise ValueError('no files matched "%s"' % filepath)

    if len(ordered_names) > 0:  # если нужен особый порядок
        all_files = files[:]
        if ordered_names.count('...') > 1:
            raise ValueError('"..." i files list can not apper more than once')
        index_by_name = dict((name, i) for i, name in enumerate(ordered_names))
        sorted_files = [None] * len(ordered_names)
        for i, file in enumerate(files):  # идём по файлам, если имя файла подошло, вынимаем этот файл из общего списка
            name = os.path.splitext(os.path.basename(file))[0]
            if name in index_by_name:
                files[i] = None
                sorted_files[index_by_name[name]] = file
        for i, file in enumerate(sorted_files):  # кидаем ошибку, если какое-то имя не было найдено
            if file is None and ordered_names[i] != '...':
                raise ValueError(('file with name "%s" not found in ' % ordered_names[i]) + ', '.join(all_files))
        if '...' in index_by_name:  # добавляем все оставшиеся файлы
            files = [f for f in files if f is not None]  # выше были вписаны None, очищаем
            index = index_by_name['...']
            sorted_files = sorted_files[:index] + files + sorted_files[index+1:]
        files = sorted_files
    return files


def get_file_type(filename):
    if filename.endswith('.css'):
        return 'text/css'
    if filename.endswith('.styl'):
        return 'text/stylus'
    raise ValueError('unknown type of file "%s"' % filename)


@register.simple_tag
def javascript(filepath, *ordered_names):
    """ Подключает ЖС-файлы, т.е. вставляет в шаблон строку/строки типа
        '<script src="/static/some/file.js"></script>'
        В пути к файлу можно использовать glob'ы, файлы сортируются по алфавиту (по полному пути, НЕ по имени).
        Следующими аргументами можно указать имена файлов, эти файлы будут соответственно упорядочены.
        "..." в списке имён означает "все остальные файлы".
        Пример:
            {% javascript "some/file.js" %}
            {% javascript "some/*.js" %} все ЖСы из папки
            {% javascript "some/*.js" "first" "second" %} два ЖСа из папки, первым будет /static/some/first.js
            {% javascript "some/*.js" "first" "..." "last" %} все ЖСы из папки, первым будет /static/some/first.js,
                                                              последним - /static/some/last.js """
    files = find_files(filepath, ordered_names)
    return format_html(('<script src="{}"></script>\n'*len(files)).strip(), *files)


@register.simple_tag
def stylesheet(filepath, *ordered_names):
    """ Подключает стили, т.е. вставляет в шаблон строку/строки типа
        <link type="text/css" rel="stylesheet" href="some/style.css">
        type выбирается по расширению файла (для .styl будет text/stylus).
        В остальном аналогичен тегу javascript. """
    files = find_files(filepath, ordered_names)
    args = [arg for file in files for arg in (get_file_type(file), file)]
    return format_html(('<link type="{}" rel="stylesheet" href="{}">\n'*len(files)).strip(), *args)
