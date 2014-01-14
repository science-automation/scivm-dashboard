from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from jobs.models import Job


class JobList(ListView):
    model = Job
    queryset = Job.objects.filter(Q(group__isnull=True) | Q(is_group_entry=True)).select_related("group").order_by("-jid")
    paginate_by = 25
    allow_empty = True
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(JobList, self).dispatch(*args, **kwargs)
    
    def get_queryset(self):
        return super(JobList, self).get_queryset().filter(owner__pk=self.request.user.pk)
    
    def get_context_data(self, **kwargs):
        ctx = super(JobList, self).get_context_data(**kwargs)
        return ctx


class JobDetail(DetailView):
    model = Job
    queryset = Job.objects.select_related("group")
    subjobs_paginate_by = 25
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(JobDetail, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return super(JobDetail, self).get_queryset().filter(owner__pk=self.request.user.pk)
    
    def get_context_data(self, **kwargs):
        ctx = super(JobDetail, self).get_context_data(**kwargs)
        job = ctx['job']
        if job.is_group_entry:
            ctx["subjobs_paginator"] = Paginator(Job.objects.for_group(job.group.pk), self.subjobs_paginate_by)
            ctx["subjobs_page"] = ctx["subjobs_paginator"].page(self.request.GET.get('page', 1))
        return ctx
