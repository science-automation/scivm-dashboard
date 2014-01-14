from django import forms
from bucket.models import Bucket
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Button
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, FormActions
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

class BucketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BucketForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                'name',
                'description',
                'owner',
            ),
            FormActions(
                Submit('save', _('Add'), css_class="btn btn-lg btn-success"),
            )
        )
        self.helper.form_id = 'form-add-bucket'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = reverse('bucket.views.add_bucket')

    class Meta:
        model = Bucket
        fields = ('name', 'description')
        exclude = ["owner"]

