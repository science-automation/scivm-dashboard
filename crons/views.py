from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from crons.models import Cron
from crons.forms import CronForm

@login_required
def index(request):
    thisuser = User.objects.get(username=request.user.username)
    crons = Cron.objects.filter(owner__pk=thisuser.pk)
    ctx = {
        'crons': crons
    }
    return render_to_response('crons/index.html', ctx,
        context_instance=RequestContext(request))

@login_required
def add_cron(request):
    form = CronForm()
    if request.method == 'POST':
        form = CronForm(request.POST)
        form.owner = request.user
        if form.is_valid():
            ptype = form.save(commit=False)
            ptype.owner = request.user
            ptype.save()
            return redirect(reverse('crons.views.index'))
    ctx = {
        'form': form
    }
    return render_to_response('crons/add_cron.html', ctx,
        context_instance=RequestContext(request))

@login_required
def enable_cron(request, cron_id):
    h = Cron.objects.get(id=cron_id)
    h.enabled = True
    h.save()
    messages.add_message(request, messages.INFO, _('Enabled') + ' {0}'.format(
        h.name))
    return redirect('crons.views.index')

@login_required
def disable_cron(request, cron_id):
    h = Cron.objects.get(id=cron_id)
    h.enabled = False
    h.save()
    messages.add_message(request, messages.INFO, _('Disabled') + ' {0}'.format(
        h.name))
    return redirect('crons.views.index')

@login_required
def remove_cron(request, cron_id):
    h = Cron.objects.get(id=cron_id)
    h.delete()
    messages.add_message(request, messages.INFO, _('Removed') + ' {0}'.format(
        h.name))
    return redirect('crons.views.index')

