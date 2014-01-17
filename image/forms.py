from django import forms
from image.models import Image
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Button
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, FormActions
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

class ImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
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
        self.helper.form_id = 'form-add-image'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = reverse('image.views.add_image')

    class Meta:
        model = Image
        fields = ('name', 'description')

