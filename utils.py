
from pony.orm import db_session
from ._compact import text_type
from wtforms import validators
from pony.orm.core import  EntityMeta



def get_attrs(entity: EntityMeta):
    return entity._attrs_


def get_attrs_dict(entity: EntityMeta) -> dict:
    return entity._adict_


def get_attr(entity: EntityMeta, attr_name: str):
    return entity._adict_.get(attr_name, None)


def get_pk_attrs(entity: EntityMeta):
    return entity._pk_attrs_


def get_obj(entity: EntityMeta, pk: tuple):
    pk_attrs = get_pk_attrs(entity)
    kwargs = {}
    for x in range(0, len(pk_attrs)):
        name = pk_attrs[x].name
        kwargs[name] = pk[x]
    #	print(kwargs, type(kwargs))
    #print ( str (** kwargs ))
    return entity.get(**kwargs)


def get_attr_entity_class(attr):
    cls = getattr(attr, "entity")
    if cls:
        return cls
    cls = getattr(attr, "_entity_")
    return cls


def entity_as_choice(entity):
    # TODO what abiout composite primary keys
    _pk_columns_ = entity._pk_columns_
    # TODO
    value = str(getattr(entity, _pk_columns_[0]))
    label = str(entity)
    #print("val", value)
    #print("label", label)
    if hasattr(entity, "__str__"):
        fun = getattr(entity, "__str__")
        if fun and hasattr(fun, '__call__'):
            label = fun()
    choice = (value, label)
    return choice


class ValueRequired(object):
    """
    Custom validation class that differentiates between false-y values and
    truly blank values. See the implementation of DataRequired and
    InputRequired -- this class sits somewhere in the middle of them.
    """
    field_flags = ('required',)

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if field.data is None or isinstance(field.data, text_type) \
           and not field.data.strip():
            message = self.message or field.gettext(
                'This field is required. <No Value>')
            field.errors[:] = []
            raise validators.StopValidation(message)


class UniqueValidator(object):

    def __init__(self, entity, attr_name, message=None):
        self.entity = entity
        self.attr_name = attr_name
        self.message = "This field should be Unique, Previous entry with the same value already existed"
        if message:
            self.message = message

    def __call__(self, form, field):
        with db_session:
            name = self.attr_name
            if self.entity.select(lambda o: getattr(o, name) == field.data).first():
                field.errors[:] = []
                raise validators.StopValidation(message=self.message)
