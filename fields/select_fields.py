
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
    'SelectChoicesField', 'BooleanSelectField',
)


class BooleanSelectField(fields.SelectFieldBase):
    widget = widgets.Select()

    def iter_choices(self):
        yield ('1', 'True', self.data)
        yield ('', 'False', not self.data)

    def process_data(self, value):
        try:
            self.data = bool(value)
        except (ValueError, TypeError):
            self.data = None

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = bool(valuelist[0])
            except ValueError:
                raise ValueError(self.gettext(
                    u'Invalid Choice: could not coerce'))


class SelectChoicesField(fields.SelectField):
    widget = ChosenSelectWidget()

    # all of this exists so i can get proper handling of None
    def __init__(self, entity=None, label=None, validators=None, coerce=text_type, choices=None, allow_blank=False, blank_text=u'', **kwargs):
        super(SelectChoicesField, self).__init__(
            label, validators, coerce, choices, **kwargs)
        self.entity = entity
        self.allow_blank = allow_blank
        self.blank_text = blank_text or '----------------'

    def iter_choices(self):
        if self.allow_blank:
            yield (u'__None', self.blank_text, self.data is None)

        for value, label in self.choices:
            yield (value, label, self.coerce(value) == self.data)

    def process_data(self, value):
        if value is None:
            self.data = None
        else:
            try:
                self.data = self.coerce(value)
                if self.entity:
                    self.data = self.entity[self.data]
            except (ValueError, TypeError):
                self.data = None

    def process_formdata(self, valuelist):
        if valuelist:
            if valuelist[0] == '__None':
                self.data = None
            else:
                try:
                    self.data = self.coerce(valuelist[0])
                except ValueError:
                    raise ValueError(self.gettext(
                        u'Invalid Choice: could not coerce'))

    def pre_validate(self, form):
        if self.allow_blank and self.data is None:
            return
        super(SelectChoicesField, self).pre_validate(form)
