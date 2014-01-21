from django import forms
from environment.models import Environment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Button
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, FormActions
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

class EnvironmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EnvironmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                'name',
                'description',
                'public',
            ),
            FormActions(
                Submit('save', _('Add'), css_class="btn btn-lg btn-success"),
            )
        )
        self.helper.form_id = 'form-add-environment'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = reverse('environment.views.add_environment')

    class Meta:
        model = Environment
        fields = ('name', 'description','public')


class EditEnvironmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditEnvironmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                'name',
                'description',
                'public',
            ),
            FormActions(
                Submit('save', _('Edit'), css_class="btn btn-lg btn-success"),
            )
        )
        self.helper.form_id = 'form-add-environment'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = reverse('environment.views.add_environment')

    class Meta:
        model = Environment
        fields = ('name', 'description','public')
