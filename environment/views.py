from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from environment.models import Environment
from image.models import Image
from accounts.models import UserProfile
from environment.forms import EnvironmentForm, EditEnvironmentForm
from scivm import tasks

@login_required
def index(request):
    """Base view
    """
    current_user = request.user
    u = UserProfile.objects.get(id=current_user.id)
    ctx = {
        'private_envs': Environment.objects.filter(owner__pk=current_user.pk),
        'favorite_envs': u.favorite_env.all(),
        'public_envs': Environment.objects.filter(public=True),
    }
    return render_to_response('environment/index.html', ctx,
        context_instance=RequestContext(request))

@login_required
def add_environment(request):
    """Add a new environment
    """
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
    """Delete an environment and it's relations to images
    """
    h = Environment.objects.get(id=environment_id)
    h.delete()
    return redirect('environment.views.index')

@login_required
def favorite_environment(request, environment_id):
    """Make an environment the favorite of this user
    """
    h = Environment.objects.get(id=environment_id)
    current_user = request.user
    u = UserProfile.objects.get(id=current_user.id)
    u.favorite_env.add(h)
    # make the environment a favorite
    return redirect('environment.views.index')

@login_required
def unfavorite_environment(request, environment_id):
    """Remove an environment from favorites
    """
    h = Environment.objects.get(id=environment_id)
    current_user = request.user
    u = UserProfile.objects.get(id=current_user.id)
    u.favorite_env.remove(h)
    # unstar environment
    return redirect('environment.views.index')

@login_required
def clone_environment(request, environment_id):
    """Clone the environment.  Makes a copy of all related images also
    """
    h = Environment.objects.get(id=environment_id)
    return redirect('environment.views.index')

@login_required
def share_environment(request, environment_id):
    """Share the environment with another user. To do: make sure a user owns it
    """
    h = Environment.objects.get(id=environment_id)
    return redirect('environment.views.index')

@login_required
def public_environment(request, environment_id):
    """Make an environment public.
    """
    h = Environment.objects.get(id=environment_id)
    h.public = True
    h.save()
    return redirect('environment.views.index')

@login_required
def private_environment(request, environment_id):
    """Make an environment private.
    """
    h = Environment.objects.get(id=environment_id)
    h.public = False
    h.save()
    return redirect('environment.views.index')

@login_required
def modify_environment(request, environment_id):
    """Not currently used
    """
    h = Environment.objects.get(id=environment_id)
    return redirect('environment.views.index')

@login_required
def edit_environment(request, environment_id):
    """Edit the name and description of the enviroment.  Associate images to an environment
    """
    h = Environment.objects.get(id=environment_id)
    current_user = request.user
    u = UserProfile.objects.get(id=current_user.id)
    initial = {
        'name': h.name,
        'description': h.description,
    }
    ctx = {
        'environment': h,
        'form': EditEnvironmentForm(initial=initial),
        'included_images': h.included_images.all(),
        'private_images': Image.objects.filter(owner__pk=current_user.pk),
        'favorite_images': u.favorite_image.all(),
    }
    return render_to_response('environment/environment_details.html', ctx,
        context_instance=RequestContext(request))

@login_required
#@owner_required # TODO
def attach_image(request, environment_id=None):
    """Relate an image to an environment
    """
    h = Environment.objects.get(id=environment_id)
    data = request.POST
    c = Container.objects.get(container_id=i)
    app.containers.add(c)
    app.save()
    return redirect(reverse('environment.views.details',
        kwargs={'app_uuid': app_uuid}))

@login_required
#@owner_required # TODO
def remove_image(request, environment_id=None, image_id=None):
    env = Environment.objects.get(id=environment_id)
    c = Container.objects.get(container_id=container_id)
    app.containers.remove(c)
    app.save()
    return redirect(reverse('environment.views.details',
        kwargs={'environment_id': environment_id}))

