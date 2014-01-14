from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from bucket.models import Bucket
from bucket.forms import BucketForm

@login_required
def index(request):
    thisuser = User.objects.get(username=request.user.username)
    buckets = Bucket.objects.filter(owner__pk=thisuser.pk)
    ctx = {
        'buckets': buckets
    }
    return render_to_response('bucket/index.html', ctx,
        context_instance=RequestContext(request))

@login_required
def add_bucket(request):
    form = BucketForm()
    if request.method == 'POST':
        form = BucketForm(request.POST)
        form.owner = request.user
        if form.is_valid():
            ptype = form.save(commit=False)
            ptype.owner = request.user
            ptype.save()
            return redirect(reverse('bucket.views.index'))
    ctx = {
        'form': form
    }
    return render_to_response('bucket/add_bucket.html', ctx,
        context_instance=RequestContext(request))

@login_required
def remove_bucket(request, bucket_id):
    h = Bucket.objects.get(id=bucket_id)
    h.delete()
    messages.add_message(request, messages.INFO, _('Removed') + ' {0}'.format(
        h.name))
    return redirect('bucket.views.index')

@login_required
def snapshot_bucket(request, bucket_id):
    h = Bucket.objects.get(id=bucket_id)
    messages.add_message(request, messages.INFO, _('Snapshot Taken') + ' {0}'.format(
        h.name))
    return redirect('bucket.views.index')


