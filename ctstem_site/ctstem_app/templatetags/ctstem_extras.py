from django import template
from django.utils.encoding import force_unicode

register = template.Library()

@register.filter
def selected_labels(form, field):
    return [label for value, label in form.fields[field].choices if value in form[field].value()]
