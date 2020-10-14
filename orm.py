from wtforms.fields.simple import SubmitField
from .utils import get_attrs
from .converter import ModelConverter
from flask_wtf import FlaskForm
from pony.orm.core import (
    EntityMeta
)


def model_fields(entity: EntityMeta, allow_pk=False, only=None, exclude=None, field_args=None, converter=None):
    """
    Generate a dictionary of fields for a given pony model.

    See `model_form` docstring for description of parameters.
    """
    converter = converter or ModelConverter()
    field_args = field_args or {}

    attrs = get_attrs(entity).copy()

    if not allow_pk:
        for a in attrs:
            if a.is_pk:
                attrs.remove(a)

    if only:
        attrs = [x for x in attrs if x.name in only]
    elif exclude:
        attrs = [x for x in attrs if x.name not in exclude]

    field_dict = {}
    for attr in attrs:
        name, field = converter.convert(
            entity,
            attr,
            field_args.get(attr.name))
        field_dict[name] = field

    return field_dict


def model_form(entity: EntityMeta, base_class=FlaskForm, allow_pk=False, only=None, exclude=None, field_args=None, converter=None, submit_kwargs={}):
    """
    Create a wtforms Form for a given pony entity class::

        from pony_wtf import model_form
        from myproject.myapp.models import User
        UserForm = model_form(User)

    :param entity:
        A pony entity class
    :param base_class:
        Base form class to extend from. Must be a ``wtforms.Form`` subclass.
    :param only:
        An optional iterable with the property names that should be included in
        the form. Only these properties will have fields.
    :param exclude:
        An optional iterable with the property names that should be excluded
        from the form. All other properties will have fields.
    :param field_args:
        An optional dictionary of field names mapping to keyword arguments used
        to construct each field object.
    :param converter:
        A converter to generate the fields based on the entity properties. If
        not set, ``ModelConverter`` is used.
    :submit_kwargs:
        Add kwargs dictionary to create submit button on the form.
        the dictionary should contain key `submit` with Truthy value
    """
    field_dict = model_fields(entity, allow_pk=allow_pk, only=only,
                              exclude=exclude, field_args=field_args, converter=converter)
    if submit_kwargs.pop("submit", False):
        name = submit_kwargs.get("name", "Submit")
        
        field_dict[name] = SubmitField(**submit_kwargs)
    
    return type(entity.__name__ + 'Form', (base_class, ), field_dict)


