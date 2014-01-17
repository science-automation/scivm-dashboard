from django import forms
from bucketstore.models import BucketStore
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Button
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, FormActions
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

class BucketStoreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BucketStoreForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                None,
                'name',
                'description',
            ),
            FormActions(
                Submit('save', _('Add'), css_class="btn btn-lg btn-success"),
            )
        )
        self.helper.form_id = 'form-add-bucketstore'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = reverse('bucketstore.views.add_bucketstore')

    class Meta:
        model = BucketStore
        fields = ('name', 'description')

