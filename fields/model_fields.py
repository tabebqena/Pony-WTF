from pony_wtf.fields.widgets import ChosenSelectWidget
from wtforms.widgets.core import Select
from .._compact import string_types
import operator

from wtforms import fields, form, widgets
from wtforms.validators import ValidationError
from .._compact import text_type

__all__ = ('ModelSelectField', 'ModelSelectMultipleField', )

class ModelSelectField(fields.SelectFieldBase):
    """
    Given Model from the database, Query will be generated as `model.select()`
    
    Specify `get_label` to customize the label associated with each option. If
    a string, this is the name of an attribute on the model object to use as
    the label text. If a one-argument callable, this callable will be passed
    model instance and expected to return the label text. Otherwise, the model
    object's `__unicode__` or `__str__` will be used.

    If `allow_blank` is set to `True`, then a blank choice will be added to the
    top of the list. Selecting this choice will result in the `data` property
    being `None`.  The label for the blank choice can be set by specifying the
    `blank_text` parameter.
    """
    widget =ChosenSelectWidget()
    def __init__(self, label=None, validators=None, **kwargs):
        self.set_label(kwargs)
        self.set_blank(kwargs)
        self.set_query(kwargs)
        self.coerce = kwargs.pop('coerce', text_type)
        super(ModelSelectField, self).__init__(label, validators, **kwargs)
        self._set_data(None)
    
    def set_label(self, kwargs):
        get_label =  kwargs.pop("get_label", None)
        if get_label is None:
            self.get_label = lambda o: text_type(o)
        elif isinstance(get_label, string_types):
            self.get_label = operator.attrgetter(get_label)
        else:
            self.get_label = get_label
    
    def set_blank(self, kwargs):
        self.allow_blank = kwargs.pop( "allow_blank", False )
        self.blank_text = kwargs.pop("blank_text", '----------------')
    
    def set_query(self, kwargs):
        self.model = kwargs.pop("model")
        self.query = self.model.select()
    
    def get_model(self, pk):
        pk = self.coerce_key(pk)
        try:
            return self.model[pk]
        except Exception as e:
            pass
            #raise e

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    def _get_data(self):
        if self._formdata:
            self._set_data(self.get_model(self._formdata))
        return self._data

    data = property(_get_data, _set_data)
    
    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0] == 'None':
                self.data = None
            else:
                self._data = None
                self._formdata = valuelist[0]
    
    def __call__(self, **kwargs):
        if 'value' in kwargs:
            self._set_data(self.get_model(kwargs['value']))
        return self.widget(self, **kwargs)

    def convert_pk(self, obj):
        key = obj.get_pk()
        if type(key) == str:
            key = "str_"+key
        else:
            key = str(key)
        return key
    
    def coerce_key(self, key):
        pk = key
        if key.startswith("str_"):
            pk = key.strip("str_")
        else:
            pk = eval(key)
        return pk
    
    def is_selected(self, key):
        return self.data == self.coerce_key(key)
    
    def iter_choices(self):
        if self.allow_blank:
            yield ('None', self.blank_text, self.data is None)

        for obj in self.query[:]:
            key = self.convert_pk(obj)
            if self.data :
                yield (key, self.get_label(obj), self.is_selected(key))  
            else:
                yield (key, self.get_label(obj), False)
        
    def pre_validate(self, form):
        if self.data is None and not self.allow_blank:
            raise ValidationError(self.gettext('Selection cannot be blank'))


class ModelSelectMultipleField(ModelSelectField):
    """
    Very similar to ModelSelectField with the difference that this will
    display a multiple select. 
    
    """
    widget = ChosenSelectWidget(multiple=True)

    def __init__(self, *args, **kwargs):
        super(ModelSelectMultipleField, self).__init__(*args, **kwargs)
    
    def get_model_list(self, _pk_list):
        pk_list = _pk_list.copy()
        l = []
        if pk_list:
            for pk in pk_list:
               pk = self.coerce_key(pk) 
               if not pk:
                   return []
               o = self.model[pk]
               l.append(o)

            return l
        return []

    def _get_data(self):
        if self._formdata is not None:
            self._set_data(self.get_model_list(self._formdata))
        return self._data or []

    def _set_data(self, data):
        self._data = data
        self._formdata = None

    data = property(_get_data, _set_data)

    def __call__(self, **kwargs):
        if 'value' in kwargs:
            self._set_data(self.get_model_list(kwargs['value']))
        return self.widget(self, **kwargs)
    
    def is_selected(self, key):
        return self.coerce_key(key) in self.data
    
    def iter_choices(self):
        if self.allow_blank:
            yield ( "None" , self.blank_text, not self.data )
        for obj in self.query[:]:
            key  = self.convert_pk(obj)  
        
            if self.data:
                yield ( key, self.get_label(obj), self.is_selected(key))
            else:
                yield ( key, self.get_label(obj), False)

    def process_formdata(self, valuelist):
        if valuelist:
            self._data = []
            self._formdata = list(map(str, valuelist))
        
    