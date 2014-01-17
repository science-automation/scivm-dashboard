from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from bucketfile.models import BucketFile
from bucketfile.forms import BucketFileForm

@login_required
def index(request):
    thisuser = User.objects.get(username=request.user.username)
    bucketfiles = BucketFile.objects.filter(owner__pk=thisuser.pk)
    ctx = {
        'bucketfiles': bucketfiles
    }
    return render_to_response('bucketfile/index.html', ctx,
        context_instance=RequestContext(request))

@login_required
def add_bucketfile(request):
    form = BucketFileForm()
    if request.method == 'POST':
        form = BucketFileForm(request.POST)
        form.owner = request.user
        if form.is_valid():
            ptype = form.save(commit=False)
            ptype.owner = request.user
            ptype.save()
            return redirect(reverse('bucketfile.views.index'))
    ctx = {
        'form': form
    }
    return render_to_response('bucketfile/add_bucketfile.html', ctx,
        context_instance=RequestContext(request))

@login_required
def remove_bucketfile(request, bucketfile_id):
    h = BucketFile.objects.get(id=bucketfile_id)
    h.delete()
    messages.add_message(request, messages.INFO, _('Removed') + ' {0}'.format(
        h.name))
    return redirect('bucketfile.views.index')

@login_required
def snapshot_bucketfile(request, bucketfile_id):
    h = BucketFile.objects.get(id=bucketfile_id)
    messages.add_message(request, messages.INFO, _('Snapshot Taken') + ' {0}'.format(
        h.name))
    return redirect('bucketfile.views.index')


