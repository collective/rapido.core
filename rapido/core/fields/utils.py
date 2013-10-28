from . import fields

def get_field_class(field_type):
    return getattr(fields, field_type.capitalize()+"Field", None)