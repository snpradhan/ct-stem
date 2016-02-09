#widgets.py
from django.forms.widgets import FileInput
from django.utils.translation import ugettext_lazy
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class NotClearableFileInput(FileInput):
    initial_text = ugettext_lazy('Currently')
    input_text = ugettext_lazy('Change')

    template_with_initial = '%(initial_text)s: %(initial)s <br />%(input_text)s: %(input)s'

    url_markup_template = '<a href="{0}">{1}</a>'

    def render(self, name, value, attrs=None):
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
