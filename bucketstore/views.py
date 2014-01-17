from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from bucketstore.models import BucketStore
from bucketstore.forms import BucketStoreForm

@login_required
def index(request):
    thisuser = User.objects.get(username=request.user.username)
    bucketstores = BucketStore.objects.filter(owner__pk=thisuser.pk)
    ctx = {
        'bucketstores': bucketstores
    }
    return render_to_response('bucketstore/index.html', ctx,
        context_instance=RequestContext(request))

@login_required
def add_bucketstore(request):
    form = BucketStoreForm()
    if request.method == 'POST':
        form = BucketStoreForm(request.POST)
        form.owner = request.user
        if form.is_valid():
            ptype = form.save(commit=False)
            ptype.owner = request.user
            ptype.save()
            return redirect(reverse('bucketstore.views.index'))
    ctx = {
        'form': form
    }
    return render_to_response('bucketstore/add_bucketstore.html', ctx,
        context_instance=RequestContext(request))

@login_required
def remove_bucketstore(request, bucketstore_id):
    h = BucketStore.objects.get(id=bucketstore_id)
    h.delete()
    messages.add_message(request, messages.INFO, _('Removed') + ' {0}'.format(
        h.name))
    return redirect('bucketstore.views.index')

@login_required
def snapshot_bucketstore(request, bucketstore_id):
    h = BucketStore.objects.get(id=bucketstore_id)
    messages.add_message(request, messages.INFO, _('Snapshot Taken') + ' {0}'.format(
        h.name))
    return redirect('bucketstore.views.index')


