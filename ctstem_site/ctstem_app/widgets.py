#widgets.py
from django.forms.widgets import FileInput
from django.utils.translation import ugettext_lazy
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django import forms
from django.forms.widgets import Select



class NotClearableFileInput(FileInput):
    initial_text = ugettext_lazy('Currently')
    input_text = ugettext_lazy('Change')

    template_with_initial = '%(initial_text)s: %(initial)s <br />%(input_text)s: %(input)s'

    url_markup_template = '<a href="{0}">{1}</a>'

    def render(self, name, value, attrs=None, renderer=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
        }
        template = '%(input)s'
        substitutions['input'] = super(NotClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html(self.url_markup_template,
                                               value.url,
                                               force_text(value))

        return mark_safe(template % substitutions)

class CheckboxSelectMultipleWithDisabledOption(forms.CheckboxSelectMultiple):

    def __init__(self, *args, **kwargs):
        self.disabled_options = kwargs.pop('disabled_options')
        super(CheckboxSelectMultipleWithDisabledOption, self).__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super(forms.CheckboxSelectMultiple, self).create_option(name, value, label, selected, index, subindex, attrs)


        if value in self.disabled_options:
            option['attrs']['disabled'] = ''

        return option

class SelectWithDisabled(Select):
    """
    Subclass of Django's select widget that allows disabling options.
    To disable an option, pass a dict instead of a string for its label,
    of the form: {'label': 'option label', 'disabled': True}
    """

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        disabled = False
        if isinstance(label, dict):
            label, disabled = label['label'], label['disabled']
        option_dict = super(SelectWithDisabled, self).create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if disabled:
            option_dict['attrs']['disabled'] = 'disabled'
        return option_dict
