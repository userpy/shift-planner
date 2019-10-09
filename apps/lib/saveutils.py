from apps.lib import AppError, MultiplayerError
from apps.lib.views import error_unless_dict, error_unless_int
from apps.lib.views import get_int_or_error, get_object_or_error, get_or_error
from contextlib import contextmanager


"""
# Usage #1:

def save_objs(json_objs, obj_ids_to_delete):
    objs = []

    # creating + updating
    for json_obj, instance, form in saveutils.process_and_save(Obj, ObjForm, json_objs, objs):
        saveutils.add_foreign(Item, json_obj, 'item', form)
        saveutils.add_foreign(Smth, json_obj, 'smth', form)

    # deleting
    saveutils.delete(Obj, obj_ids_to_delete)

    return objs


# Usage #2:

def save_objs(json_objs, obj_ids_to_delete):
    objs = []

    # creating + updating
    for json_obj in json_objs:
        saveutils.check_json_obj(Obj, json_obj)
        _, instance = saveutils.get_instance_or_none(Obj, json_obj)
        form = saveutils.get_form_and_check(Obj, json_obj, ObjForm, instance)

        # находим и добавляем объекты по внешним ключам (TODO: мб кешировать)
        with saveutils.add_foreign_with_check(Item, json_obj, 'item', form) as (item_id, item):
            do_some_checks_with(item)
        with saveutils.add_foreign_with_check(Smth, json_obj, 'smth', form) as (smth_id, smth):
            do_some_checks_with(smth)

        obj = form.save()
        objs.append(obj)

    # deleting
    with saveutils.delete_with_check(Obj, obj_ids_to_delete) as objs_to_delete_qs:
        do_some_checks_with(objs_to_delete_qs)

    return objs
"""


def check_json_obj(Model, json_obj):
    error_unless_dict(json_obj,
                      'wrong type of %s: must be "dict" but it is "%s"'
                      % (Model.__name__, type(json_obj).__name__))


def get_instance_or_none(Model, json_obj, pk_key='id'):
    if pk_key in json_obj:
        pk = json_obj[pk_key]
        error_unless_int(pk, 'wrong %s id: %s (%s)' % (Model.__name__, pk, type(pk).__name__))
        if pk < 0:
            return pk, None
        return pk, get_object_or_error(Model, pk=pk)
    return None, None


def get_form_and_check(Model, json_obj, Form, instance):
    form = Form(json_obj, instance=instance)
    if not form.is_valid():
        raise AppError('wrong %s data: %s' % (Model.__name__, dict(form.errors)))
    return form


# saveutils.must_not_change(instance, json_timesheet_data, 'department_id')
# saveutils.must_not_change(instance, form.cleaned_data, 'date', original_value=date_before)
def must_not_change(instance, json_obj_or_cleaned_data, attr_name, **kwargs):
    if instance is None:
        return
    original_value = kwargs.get('original_value', getattr(instance, attr_name))
    new_value = get_or_error(json_obj_or_cleaned_data, attr_name)
    if original_value != new_value:
        raise AppError('not allowed to change "%s" (%s -> %s) of %s #%s'
                       % (attr_name, original_value, new_value, instance.__class__.__name__, instance.pk))


@contextmanager
def add_foreign_with_check(ForeignModel, json_obj, attr_name, form, new_ids_map=None):
    pk = get_int_or_error(json_obj, attr_name+'_id', 'missing "%s_id" attribute' % attr_name)
    if new_ids_map is not None and pk < 0:
        pk = new_ids_map.get(pk, pk)
    obj = get_object_or_error(ForeignModel, pk=pk, msg_='%s #%d not found' % (ForeignModel.__name__, pk))
    yield pk, obj
    setattr(form.instance, attr_name, obj)


def add_foreign(ForeignModel, json_obj, attr_name, form, new_ids_map=None):
    with add_foreign_with_check(ForeignModel, json_obj, attr_name, form, new_ids_map) as (pk, obj):
        return pk, obj


def get_generic(foreign_types, json_obj, attr_name):
    foreign_id = get_int_or_error(json_obj, attr_name+'_id', 'missing "%s_id" attribute' % attr_name)
    foreign_type_name = str(get_or_error(json_obj, attr_name+'_type', 'missing "%s_type" attribute' % attr_name))
    try:
        foreign_type = foreign_types[foreign_type_name]
    except KeyError:
        raise AppError('wrong %s type "%s"' % (attr_name, foreign_type_name))
    return foreign_id, foreign_type


def process_and_save(Model, Form, json_objs, objs, new_ids_map=None,
                     failed_objs=[], extend_json_obj=None):
    for json_obj in json_objs:
        if extend_json_obj:
            json_obj.update(extend_json_obj)

        check_json_obj(Model, json_obj)
        pk, instance = get_instance_or_none(Model, json_obj)
        form = get_form_and_check(Model, json_obj, Form, instance)
        yield json_obj, instance, form
        try:
            obj = form.save()
        except MultiplayerError:
            failed_objs.append(json_obj)
            continue

        if new_ids_map is not None and pk is not None and pk < 0:
            new_ids_map[pk] = obj.pk
        objs.append(obj)


@contextmanager
def delete_with_check(Model, obj_ids_to_delete):
    objs_to_delete_qs = Model.objects.filter(pk__in=obj_ids_to_delete)
    yield objs_to_delete_qs
    objs_to_delete_qs.delete()


def delete(Model, obj_ids_to_delete):
    with delete_with_check(Model, obj_ids_to_delete):
        pass


"""
def common_save_func(json_objs, obj_ids_to_delete):
    objs = []
    for json_obj in json_objs:
        # check if dict
        instance = None
        # try [find] instance
        # HOOK: check_attrs(json_obj, instance)
        # create [form] and check
        # fill [foreign objects]
        obj = form.save()
        objs.append(obj)
        # HOOK: after_save(obj, json_obj)
    if len(obj_ids_to_delete) > 0:
        # delete [all]
    return objs


class Saver(object):
    def check_obj_attrs(self, json_obj, instance):
        pass

    def check_foreign_obj(self, fk, fobj, instance):
        pass

    def after_obj_save(self, obj, json_obj):
        pass

    def check_deleting(self, objs_to_delete_qs):
        pass

    def save(self, json_objs, obj_ids_to_delete):
        objs = []

        # creating + updating
        for json_obj in json_objs:
            error_unless_dict(json_obj,
                              'wrong type of %s: must be "dict" but it is "%s"'
                              % (self.name, type(json_obj).__name__))

            # если есть id, это изменение - находим instance
            instance = None
            if 'id' in json_obj:
                error_unless_int(json_obj['id'], 'wrong %s id: %d' % (self.name, json_obj['id']))
                instance = get_object_or_error(self.model, pk=json_obj['id'])

            self.check_obj_attrs(json_obj, instance)

            form = self.form(json_obj, instance=instance)
            if not form.is_valid():
                raise AppError('wrong %s data: %s' % (self.name, dict(form.errors)))

            # находим и добавляем объекты по внешним ключам (TODO: мб кешировать)
            for fk in self.foreign_keys:
                fid = get_int_or_error(json_obj, fk['name']+'_id', '%s missing "%s_id" attribute' % (self.name, fk['name']))
                fobj = get_object_or_error(fk['model'], pk=fid, msg_='%s #%d not found' % (fk['name'], fid))
                self.check_foreign_obj(fk, fobj, instance)
                setattr(form.instance, fk['name'], fobj)

            obj = form.save()
            objs.append(obj)
            self.after_obj_save(obj, json_obj)

        # deleting
        objs_to_delete_qs = self.model.objects.filter(pk__in=obj_ids_to_delete)
        self.check_deleting(objs_to_delete_qs)
        objs_to_delete_qs.delete()

        return objs
"""
