from django import forms
from jobs.models import Job
from crons.models import Cron
import json


class JobAddForm(forms.ModelForm):
    # "core_type" is sent as "type"
    type = forms.ChoiceField(initial=Job.C1, choices=Job.CORE_TYPE_DICT.items(), required=False)
    mod_versions = forms.CharField(required=True)

    class Meta:
        model = Job
        fields = (
            'hostname', 'cloud_version', 'ap_version', 'fast_serialization',
            'language', 'language_version', 
            'func_name',
            'label', 'cores', 'depends_on_errors',
            'restartable', 'max_runtime', 'profile',
            'priority', 'process_id', 'kill_process',
        )
    
    def clean_mod_versions(self):
        mod_versions = self.cleaned_data.get("mod_versions", "").replace("'", "\"")
        try:
            ret = json.loads(mod_versions)
            return ret
        except Exception, e:
            raise forms.ValidationError("mod_versions is invalid")

    def clean(self):
        data = self.cleaned_data
        if "type" in data:
            data["core_type"] = data["type"]
            del data["type"]
        return data
    
    def save(self, *args, **kwargs):
        instance = super(JobAddForm, self).save(*args, **kwargs)
        instance.mod_versions = self.cleaned_data["mod_versions"]
        return instance


class JobAddMapForm(forms.Form):
    group_id = forms.IntegerField(required=False, min_value=0) # doesn't come with first chunk
    map_len = forms.IntegerField(required=False, min_value=0)  # comes only with the first chunk
    first_maparg_index = forms.IntegerField(min_value=0)
    done = forms.BooleanField(initial=False, required=False) # comes only when its done?


class CronLabelForm(forms.ModelForm):
    
    class Meta:
        model = Cron
        fields = ('label',)


class CronAddForm(JobAddForm):

    class Meta:
        model = Cron
        fields = (
            'hostname', 'cloud_version', 'ap_version',
            'label', 'language', 'language_version', 
            'func_name', 'fast_serialization',
            'cores', 'depends_on_errors',
            'restartable', 'max_runtime', 'profile',
            'priority', 'process_id', 'kill_process',
            
            'cron_exp', 
        )
    
    def clean_cron_exp(self):
        from cloud.util.cronexpr import CronTime
        cron_exp = self.cleaned_data.get("cron_exp", "")
        try:
            CronTime(cron_exp)
        except ValueError:
            raise forms.ValidationError("cron expression is invalid")
        return cron_exp
