

"""
Useful form fields for use with the Peewee ORM.
(cribbed from wtforms.ext.django.fields)
"""
from . import ChosenSelectWidget
from .._compact import string_types
import datetime
import operator
import warnings

from wtforms import fields, form, widgets
from wtforms.fields import FormField, _unset_value
from wtforms.validators import ValidationError
from wtforms.widgets import HTMLString, html_params
from .._compact import text_type
from ..utils import get_pk_attrs

__all__ = (
    'WPTimeField', 'WPDateField',
    'WPDateTimeField',
)


class StaticAttributesMixin(object):
    attributes = {}

    def __call__(self, **kwargs):
        for key, value in self.attributes.items():
            if key in kwargs:
                curr = kwargs[key]
                kwargs[key] = '%s %s' % (value, curr)
        return super(StaticAttributesMixin, self).__call__(**kwargs)


class WPTimeField(StaticAttributesMixin, fields.StringField):
    attributes = {'class': 'time-widget'}
    formats = ['%H:%M:%S', '%H:%M']

    def _value(self):
        if self.raw_data:
            return u' '.join(self.raw_data)
        else:
            return self.data and self.data.strftime(self.formats[0]) or u''

    def convert(self, time_str):
        for format in self.formats:
            try:
                return datetime.datetime.strptime(time_str, format).time()
            except ValueError:
                pass

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = self.convert(' '.join(valuelist))
            if self.data is None:
                raise ValueError(self.gettext(u'Not a valid time value'))


class WPDateField(StaticAttributesMixin, fields.DateField):
    attributes = {'class': 'date-widget'}


def datetime_widget(field, **kwargs):
    kwargs.setdefault('id', field.id)
    kwargs.setdefault('class', '')
    kwargs['class'] += ' datetime-widget'
    html = []
    for subfield in field:
        html.append(subfield(**kwargs))
    return HTMLString(u''.join(html))


def generate_datetime_form(validators=None):
    class _DateTimeForm(form.Form):
        date = WPDateField(validators=validators)
        time = WPTimeField(validators=validators)
    return _DateTimeForm


class WPDateTimeField(FormField):
    widget = staticmethod(datetime_widget)

    def __init__(self, label='', validators=None, **kwargs):
        DynamicForm = generate_datetime_form(validators)
        super(WPDateTimeField, self).__init__(
            DynamicForm, label, validators=None, **kwargs)

    def process(self, formdata, data=_unset_value):
        prefix = self.name + self.separator
        kwargs = {}
        if data is _unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        if data and data is not _unset_value:
            kwargs['date'] = data.date()
            kwargs['time'] = data.time()

        self.form = self.form_class(formdata, prefix=prefix, **kwargs)

    def populate_obj(self, obj, name):
        setattr(obj, name, self.data)

    @property
    def data(self):
        date_data = self.date.data
        time_data = self.time.data or datetime.time(0, 0)
        if date_data:
            return datetime.datetime.combine(date_data, time_data)


