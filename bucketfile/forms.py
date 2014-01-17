from django import forms
from bucketfile.models import BucketFile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Button
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, FormActions
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

class BucketFileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BucketFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                'owner',
                'name',
                'size',
                'public',
            ),
            FormActions(
                Submit('save', _('Add'), css_class="btn btn-lg btn-success"),
            )
        )
        self.helper.form_id = 'form-add-bucketfile'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = reverse('bucketfile.views.add_bucketfile')

    class Meta:
        model = BucketFile
        fields = ('name', 'size','public')
        exclude = ["owner"]

