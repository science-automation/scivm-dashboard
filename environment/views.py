from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from environment.models import Environment
from accounts.models import UserProfile
from environment.forms import EnvironmentForm
from scivm import tasks

@login_required
def index(request):
    thisuser = User.objects.get(username=request.user.username)
    s = UserProfile.objects.get(id=1)
    ctx = {
        'private_envs': Environment.objects.filter(owner__pk=thisuser.pk),
        'favorite_envs': s.favorite_env.all(),
        'public_envs': Environment.objects.filter(public=True),
    }
    return render_to_response('environment/index.html', ctx,
        context_instance=RequestContext(request))

@login_required
def add_environment(request):
    form = EnvironmentForm()
    if request.method == 'POST':
        form = EnvironmentForm(request.POST)
        if form.is_valid():
            ptype = form.save(commit=False)
            ptype.owner = request.user
            ptype.save()
            return redirect(reverse('environment.views.index'))
    ctx = {
        'form': form
    }
    return render_to_response('environment/add_environment.html', ctx,
        context_instance=RequestContext(request))

@login_required
def remove_environment(request, environment_id):
    h = Environment.objects.get(id=environment_id)
    h.delete()
    return redirect('environment.views.index')

@login_required
def favorite_environment(request, environment_id):
    """Make an environment the favorite of this user
    """
    h = Environment.objects.get(id=environment_id)
    u = UserProfile.objects.get(id=1)
    u.favorite_env.add(h)
    # make the environment a favorite
    return redirect('environment.views.index')

@login_required
def unfavorite_environment(request, environment_id):
    """Remove an environment from favorites
    """
    h = Environment.objects.get(id=environment_id)
    u = UserProfile.objects.get(id=1)
    u.favorite_env.remove(h)
    # unstar environment
    return redirect('environment.views.index')

@login_required
def clone_environment(request, environment_id):
    h = Environment.objects.get(id=environment_id)
    # clone the environment
    return redirect('environment.views.index')

@login_required
def share_environment(request, environment_id):
    """Share the environment with another user. To do: make sure a user owns it
    """
    h = Environment.objects.get(id=environment_id)
    return redirect('environment.views.index')

@login_required
def public_environment(request, environment_id):
    """Make an environment public. To do: make sure a user owns it
    """
    h = Environment.objects.get(id=environment_id)
    h.public = True
    h.save()
    return redirect('environment.views.index')

@login_required
def private_environment(request, environment_id):
    """Make an environment private.  To do: make sure user owns it
    """
    h = Environment.objects.get(id=environment_id)
    h.public = False
    h.save()
    return redirect('environment.views.index')

@login_required
def modify_environment(request, environment_id):
    h = Environment.objects.get(id=environment_id)
    # clone the environment
    return redirect('environment.views.index')

@login_required
def edit_info_environment(request, environment_id):
    h = Environment.objects.get(id=environment_id)
    # edit the environments info
    return redirect('environment.views.index')
