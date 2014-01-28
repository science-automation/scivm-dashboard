# Copyright 2014 Science Automation
#
# This file is part of Science VM.
#
# Science VM is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Science VM is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Science VM. If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from provider.models import Provider
from provider.forms import ProviderForm

@login_required
def index(request):
    thisuser = User.objects.get(username=request.user.username)
    providers = Provider.objects.filter(owner__pk=thisuser.pk)
    ctx = {
        'providers': providers
    }
    return render_to_response('provider/index.html', ctx,
        context_instance=RequestContext(request))

@login_required
def add_provider(request):
    form = ProviderForm()
    if request.method == 'POST':
        form = ProviderForm(request.POST)
        if form.is_valid():
            ptype = form.save(commit=False)
            ptype.owner = request.user
            ptype.save()
            return redirect(reverse('provider.views.index'))
    ctx = {
        'form': form
    }
    return render_to_response('provider/add_provider.html', ctx,
        context_instance=RequestContext(request))

@login_required
def remove_provider(request, provider_id):
    h = Provider.objects.get(id=provider_id)
    h.delete()
    messages.add_message(request, messages.INFO, _('Removed') + ' {0}'.format(
        h.name))
    return redirect('provider.views.index')

@login_required
def snapshot_provider(request, provider_id):
    h = Provider.objects.get(id=provider_id)
    messages.add_message(request, messages.INFO, _('Snapshot Taken') + ' {0}'.format(
        h.name))
    return redirect('provider.views.index')


