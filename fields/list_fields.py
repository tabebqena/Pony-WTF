
from wtforms import (
    StringField,
    IntegerField,
    FloatField,
    FieldList
)

class IntListField(FieldList):
    def __init__(self, label=None, validators=None, min_entries=0,
                 max_entries=None, default=tuple(), **kwargs):
        super(IntListField, self).__init__(
            IntegerField,
            label, validators, min_entries=min_entries,
            max_entries=max_entries, default=default, **kwargs)


class FloatListField(FieldList):
    def __init__(self, label=None, validators=None, min_entries=0,
                 max_entries=None, default=tuple(), **kwargs):
        super(FloatListField, self).__init__(
            FloatField,
            label, validators, min_entries=min_entries,
            max_entries=max_entries, default=default, **kwargs)


class StrListField(FieldList):
    def __init__(self, label=None, validators=None, min_entries=0,
                 max_entries=None, default=tuple(), **kwargs):
        super(StrListField, self).__init__(
            StringField,
            label, validators, min_entries=min_entries,
            max_entries=max_entries, default=default, **kwargs)
