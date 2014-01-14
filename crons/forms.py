from django import forms
from crons.models import Cron
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Button
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, FormActions
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

class CronForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CronForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                'label',
                'cron_exp',
                'func_name',
                'owner',
            ),
            FormActions(
                Submit('save', _('Add'), css_class="btn btn-lg btn-success"),
            )
        )
        self.helper.form_id = 'form-add-cron'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = reverse('crons.views.add_cron')

    class Meta:
        model = Cron
        fields = ('label', 'cron_exp', 'func_name', 'owner')
        exclude = ["owner"]

