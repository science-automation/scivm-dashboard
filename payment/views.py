from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from environment.models import Environment
from environment.forms import EnvironmentForm

@login_required
def index(request):
    environment = Environment.objects.all()
    ctx = {
        'environment': environment
    }
    return render_to_response('payment/index.html', ctx,
        context_instance=RequestContext(request))
