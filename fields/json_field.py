
from wtforms.fields.core import Field
from pony_wtf.fields.widgets import JsonWidget
from wtforms import fields
import json


class JSONFieldBase(Field):
    widget = JsonWidget()
    default = '{}'    
                
    def _value(self):
        val = self.data if self.data else '{}'
        return self.beutify( eval(val))

    def process_formdata(self, valuelist):
        if valuelist:
            text = valuelist[0]

            try:
                text = eval(text)                
            except Exception :
                raise ValueError("Invalid input")
            
            try:
                self.data = json.dumps(text)
            except ValueError:
                raise ValueError('This field contains invalid JSON')
            
        else:
            self.data = None
    
    def beutify(self, data):
        print ("beutify:", self.json_attrs)
        return json.dumps(data, sort_keys=self.json_attrs.get("sort_keys"), indent=self.json_attrs.get("indent"))
        
        
    def pre_validate(self, form):
        super(JSONFieldBase, self).pre_validate(form)
        if self.data:
            try:
                json.dumps(self.data)
            except TypeError:
                raise ValueError('This field contains invalid JSON')


class JSONField(JSONFieldBase):
    def __init__(self, label=None, validators=None, filters=tuple(),
                 description='', id=None, default=None, widget=None,
                 render_kw=None, _form=None, _name=None, _prefix='',
                 _translations=None, _meta=None, json_attrs={}):
        default_attrs = {
            "sort_keys": True,
            "indent": 4
        }
        print (56, json_attrs)
        if not json_attrs:
            print (158)
            self.json_attrs = default_attrs.copy()
        else :
            print (61)
            self.json_attrs= {}
            self.json_attrs.update(json_attrs)
        print(60, self.json_attrs)
        if not render_kw :
            render_kw = {"rows": 20 }
        super(JSONField, self).__init__(label, validators, filters, description, id, default, widget, render_kw, _form, _name, _prefix, _translations, _meta)
