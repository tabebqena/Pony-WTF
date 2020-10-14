"""
Tools for generating forms based on Django models.
"""
import datetime
import decimal
import uuid
from collections import OrderedDict, namedtuple

from pony.orm.core import EntityMeta
from pony.orm.ormtypes import (FloatArray, IntArray, Json, LongStr,                     LongUnicode, StrArray)
from wtforms import fields as wtf_fields
from wtforms import validators
from wtforms.fields.core import DecimalField, FloatField, IntegerField, StringField
from wtforms.fields.html5 import DateField, DateTimeField, TimeField
from wtforms.fields.simple import TextAreaField



from ._compact import text_type
from .fields import (BooleanSelectField, FloatListField, IntListField,
                     ModelSelectField, ModelSelectMultipleField,
                     SelectChoicesField, StrListField, JSONField)
from .utils import get_attr_entity_class,  UniqueValidator, ValueRequired

FieldInfo = namedtuple('FieldInfo', ('name', 'field'))


def handle_null_filter(data):
    if data == '':
        return None
    return data


default_converters = OrderedDict((
    #   Standard types
    (text_type, StringField),
    (int, IntegerField),
    (float, FloatField),
    (decimal.Decimal, DecimalField),
    #   Dates, times
    (datetime.date, DateField  # WPDateField
     ),
    (datetime.datetime, DateTimeField  # WPDateTimeField
     ),
    (datetime.time, TimeField  # WPTimeField
     ),
    (bool, BooleanSelectField),

    (LongStr, TextAreaField),
    (LongUnicode, TextAreaField),
    (uuid.UUID, StringField),

    (IntArray, IntListField),
    (StrArray, StrListField),
    (FloatArray, FloatListField),
    (Json, JSONField)

))


coerce_defaults = {
    int: int,
    str: text_type,
    decimal: float,
}



class ModelConverter(object):
    """convert entity attribute to Wtf-Field
    """
    def __init__(self, additional=None, additional_coerce=None, overrides=None):
        self.converters = {}
        
        if additional:
            self.converters.update(additional)

        self.coerce_settings = dict( coerce_defaults )
        if additional_coerce:
            self.coerce_settings.update(additional_coerce)
        self.overrides = overrides or {}
    
    def set_required_validator(self,  attr, kwargs):
        if attr.is_required:
            kwargs['validators'].append(validators.Required())
        else :
            kwargs['validators'].append(validators.Optional())
            # further 
            if attr.is_relation:
                pass
            else:                
                if (attr.nullable or (attr.default is not None)) :
                    kwargs['validators'].append(validators.Optional())
                else:
                    kwargs['validators'].append(ValueRequired())
    
    def set_unique_validator(self, entity, attr, kwargs):
        if attr.is_unique :
            kwargs['validators'].append(UniqueValidator(entity, attr.name))
        
    
    def add_null_filter(self, attr, kwargs):
        if not attr.is_required and attr.nullable:
            # Treat empty string as None when converting.
            kwargs['filters'].append(handle_null_filter)
    
    def is_filter_allowed(self, field, kwargs):
        if issubclass(field,  wtf_fields.FormField):
            kwargs.pop('filters')    
    
    def build_kwargs(self, entity, attr, field_args):        
        field_args = field_args or {}
        kwargs = {
            'label': attr.name,
            'validators': [],
            'filters': [],
            'default': attr.default,
            #'description': attr.help_text
        }
        if field_args:
            kwargs.update(field_args)
        #  {"validators": [Email], "only_validators": True }
        if  not kwargs.pop("only_validators", False):
            self.set_required_validator(attr, kwargs)
            self.set_unique_validator(entity, attr , kwargs)
        self.add_null_filter(attr, kwargs)
        return kwargs
    
    def get_custom(self, entity, attr, kwargs):
        if attr.name in self.overrides:
            self.is_filter_allowed(self.overrides[attr.name], kwargs)
            return FieldInfo(attr.name, self.overrides[attr.name](**kwargs))

        if hasattr(attr, 'wtf_field'):
            self.is_filter_allowed(attr.wtf_field(entity, **kwargs), kwargs)
            return FieldInfo(attr.name, attr.wtf_field(entity, **kwargs))
    
    def handle_select_fields(self,attr, kwargs):
        choices = kwargs.pop('choices',
                               getattr(attr, 'kwargs', []))
        coerce_fn = None
        for converter in default_converters:
            if converter in self.coerce_settings:
                coerce_fn = self.coerce_settings[converter]
            if 'coerce' in kwargs:
                coerce_fn = kwargs.pop('coerce',
                                        self.coerce_settings[converter])
        allow_blank = kwargs.pop(
            'allow_blank', not attr.is_required)
        kwargs.update({
            'choices': choices,
            'coerce': coerce_fn,
            'allow_blank': allow_blank})
        return FieldInfo(attr.name, SelectChoicesField(**kwargs))
    
    def convert(self, entity: EntityMeta, attr, field_args):
        """return Wtf-Field based on the entity attribute given

        Args:
            entity (EntityMeta): [The class of the db.entity  ]
            
            attr ([type]): 
            [the attribute instance ]
            field_args ([type]): [Arguments ]

        Raises:
            AttributeError: [description]

        Returns:
            [type]: [description]
        """
        kwargs = self.build_kwargs( entity, attr ,field_args, )
        custom = self.get_custom(entity, attr, kwargs)
        if custom:
            return custom
        # converter : { attr_type: fieldInfo }
        for converter in self.converters:
            if isinstance(attr, converter):
                self.is_filter_allowed(
                    self.converters[converter], kwargs)
                return self.converters[converter](entity, attr, **kwargs)
                
        if "choices" in kwargs or 'choices' in attr.kwargs :
            self.is_filter_allowed(attr.wtf_field(entity, **kwargs), kwargs)
            return self.handle_select_fields(attr, kwargs)
        if attr.is_relation :
            coerce_fn  = None
            for converter in default_converters:
                if converter in self.coerce_settings:
                    coerce_fn = self.coerce_settings[converter]
                if 'coerce' in kwargs:
                    coerce_fn = kwargs.pop('coerce',
                                            self.coerce_settings[converter])
            allow_blank = kwargs.pop('allow_blank', not attr.is_required)
            model = get_attr_entity_class(attr.reverse)
            kwargs.update({
                # fix bug , 
                #'coerce': coerce_fn,
                'allow_blank': allow_blank,
                'model': model,
                })  
            
            if attr.is_collection :
                return FieldInfo(attr.name, 
                                    # label=None, validators=None, model=None, **kwargs
                                    ModelSelectMultipleField(**kwargs))
            else:
                return FieldInfo(attr.name, ModelSelectField(**kwargs))
        
        try:           
            converter = default_converters[attr.py_type]
        except Exception:
            raise AttributeError("There is not possible conversion for '%s' " % type(attr.py_type))
        self.is_filter_allowed( converter, kwargs)
        return FieldInfo(attr.name, converter(**kwargs))
