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

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.template.response import TemplateResponse
from django import http

from environment.models import Environment
from image.models import Image
from environment.forms import EnvironmentForm, EditEnvironmentForm
from scivm import tasks


@login_required
def index(request):
    """Base view
    """
    ctx = {
        'private_envs': Environment.objects.for_user_id(request.user.pk),
        'favorite_envs': request.user.favorite_env.all(),
        'public_envs': Environment.objects.filter(public=True), #FIXME this can be large, very large
    }
    return TemplateResponse(request, 'environment/index.html', ctx)


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
    return TemplateResponse(request, 'environment/add_environment.html', ctx)


@login_required
def remove_environment(request, environment_id):
    """Delete an environment and it's relations to images
    """
    try:
        h = Environment.objects.for_user_id(request.user.id).get(id=environment_id)
    except Environment.DoesNotExist:
        raise http.Http404
    h.delete()
    return redirect('environment.views.index')


@login_required
def favorite_environment(request, environment_id):
    """Make an environment the favorite of this user
    """
    try:
        h = Environment.objects.avail_for_user_id(request.user.id).get(id=environment_id)
    except Environment.DoesNotExist:
        raise http.Http404
    
    request.user.favorite_env.add(h)
    # make the environment a favorite
    return redirect('environment.views.index')


@login_required
def unfavorite_environment(request, environment_id):
    """Remove an environment from favorites
    """
    try:
        h = Environment.objects.get(id=environment_id)
    except Environment.DoesNotExist:
        raise http.Http404
    
    request.user.favorite_env.remove(h)
    # unstar environment
    return redirect('environment.views.index')


@login_required
def clone_environment(request, environment_id):
    """Clone the environment.  Makes a copy of all related images also
    """
    try:
        h = Environment.objects.avail_for_user_id(request.user.id).get(id=environment_id)
    except Environment.DoesNotExist:
        raise http.Http404
    #TODO
    return redirect('environment.views.index')


@login_required
def share_environment(request, environment_id):
    """Share the environment with another user. To do: make sure a user owns it
    """
    try:
        h = Environment.objects.for_user_id(request.user.id).get(id=environment_id)
    except Environment.DoesNotExist:
        raise http.Http404
    #TODO
    return redirect('environment.views.index')


@login_required
def public_environment(request, environment_id):
    """Make an environment public.
    """
    try:
        h = Environment.objects.for_user_id(request.user.id).get(id=environment_id)
    except Environment.DoesNotExist:
        raise http.Http404
    h.public = True
    h.save()
    return redirect('environment.views.index')


@login_required
def private_environment(request, environment_id):
    """Make an environment private.
    """
    try:
        h = Environment.objects.for_user_id(request.user.id).get(id=environment_id)
    except Environment.DoesNotExist:
        raise http.Http404
    h.public = False
    h.save()
    return redirect('environment.views.index')


@login_required
def modify_environment(request, environment_id):
    """Not currently used
    """
    try:
        h = Environment.objects.for_user_id(request.user.id).get(id=environment_id)
    except Environment.DoesNotExist:
        raise http.Http404
    #TODO
    return redirect('environment.views.index')


@login_required
def edit_environment(request, environment_id):
    """Edit the name and description of the enviroment.  Associate images to an environment
    """
    try:
        h = Environment.objects.for_user_id(request.user.id).get(id=environment_id)
    except Environment.DoesNotExist:
        raise http.Http404
    
    if request.method == 'POST':
        form = EnvironmentForm(request.POST, instance=h)
        if form.is_valid():
            ptype = form.save(commit=False)
            ptype.save()
            return redirect(reverse('environment.views.index'))
    
    ctx = {
        'environment': h,
        'form': EditEnvironmentForm(instance=h),
        'included_images': h.included_images.all(),
        'private_images': Image.objects.for_user_id(request.user.pk),
        'favorite_images': request.user.favorite_image.all(),
    }
    return TemplateResponse(request, 'environment/environment_details.html', ctx)


@login_required
#@owner_required # TODO
def attach_image(request, environment_id=None, image_id=None):
    """Relate an image to an environment
    """
    env = Environment.objects.get(id=environment_id)
    i = Image.objects.get(id=image_id)
    i.environments.add(env)
    env.save()
    return redirect(reverse('environment.views.edit_environment',
        kwargs={'environment_id': environment_id}))


@login_required
#@owner_required # TODO
def unattach_image(request, environment_id=None, image_id=None):
    """Unrelate an image to an environment
    """
    env = Environment.objects.get(id=environment_id)
    i = Image.objects.get(id=image_id)
    i.environments.remove(env)
    env.save()
    return redirect(reverse('environment.views.edit_environment',
        kwargs={'environment_id': environment_id}))

