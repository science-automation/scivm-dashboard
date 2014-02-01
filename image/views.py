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
from django.template.response import TemplateResponse
from django import http
from django.contrib import messages
from django.utils.translation import ugettext as _
from image.models import Image
from image.forms import ImageForm, EditImageForm
from scivm import tasks


@login_required
def index(request):
    ctx = {
        'private_images': Image.objects.filter(owner__pk=request.user.pk),
        'favorite_images': request.user.favorite_image.all(),
        'public_images': Image.objects.filter(public=True), #FIXME this can be very large
    }
    return TemplateResponse(request, 'image/index.html', ctx)


@login_required
def add_image(request):
    form = ImageForm()
    if request.method == 'POST':
        form = ImageForm(request.POST)
        if form.is_valid():
            ptype = form.save(commit=False)
            ptype.owner = request.user
            ptype.save()
            return redirect(reverse('image.views.index'))
    ctx = {
        'form': form
    }
    return TemplateResponse(request, 'image/add_image.html', ctx)


@login_required
def remove_image(request, image_id):
    try:
        h = Image.objects.for_user_id(request.user.id).get(id=image_id)
    except Image.DoesNotExist:
        raise http.Http404

    h.delete()
    messages.add_message(request, messages.INFO, _('Removed') + ' {0}'.format(
        h.name))
    return redirect('image.views.index')


@login_required
def favorite_image(request, image_id):
    """Make an image the favorite of this user
    """
    try:
        h = Image.objects.avail_for_user_id(request.user.id).get(id=image_id)
    except Image.DoesNotExist:
        raise http.Http404
    
    request.user.favorite_image.add(h)
    # make the image a favorite
    return redirect('image.views.index')


@login_required
def unfavorite_image(request, image_id):
    """Remove an image from favorites
    """
    try:
        h = Image.objects.get(id=image_id)
    except Image.DoesNotExist:
        raise http.Http404
    
    request.user.favorite_image.remove(h)
    # unstar image
    return redirect('image.views.index')


@login_required
def clone_image(request, image_id):
    try:
        h = Image.objects.avail_for_user_id(request.user.id).get(id=image_id)
    except Image.DoesNotExist:
        raise http.Http404
    
    #TODO clone the image
    return redirect('image.views.index')

@login_required
def share_image(request, image_id):
    """Share the image with another user. To do: make sure a user owns it
    """
    try:
        h = Image.objects.for_user_id(request.user.id).get(id=image_id)
    except Image.DoesNotExist:
        raise http.Http404
    #TODO 
    return redirect('image.views.index')

@login_required
def public_image(request, image_id):
    """Make an image public. To do: make sure a user owns it
    """
    try:
        h = Image.objects.for_user_id(request.user.id).get(id=image_id)
    except Image.DoesNotExist:
        raise http.Http404
    
    h.public = True
    h.save()
    return redirect('image.views.index')

@login_required
def private_image(request, image_id):
    """Make an image private.  To do: make sure user owns it
    """
    try:
        h = Image.objects.for_user_id(request.user.id).get(id=image_id)
    except Image.DoesNotExist:
        raise http.Http404
    
    h.public = False
    h.save()
    return redirect('image.views.index')

@login_required
def modify_image(request, image_id):
    #FIXME permissions,  what can be cloned?
    try:
        h = Image.objects.for_user_id(request.user.id).get(id=image_id)
    except Image.DoesNotExist:
        raise http.Http404
    # clone the image
    return redirect('image.views.index')

@login_required
def edit_image(request, image_id):
    """Edit the name and description of the enviroment.  Associate images to an image
    """
    try:
        h = Image.objects.for_user_id(request.user.id).get(id=image_id)
    except Image.DoesNotExist:
        raise http.Http404
    
    if request.method == 'POST':
        form = ImageForm(request.POST, instance=h)
        if form.is_valid():
            ptype = form.save(commit=False)
            ptype.save()
            return redirect(reverse('image.views.index'))
    ctx = {
        'image': h,
        'form': EditImageForm(instance=h),
    }
    return TemplateResponse(request, 'image/image_details.html', ctx)

@login_required
def import_image(request):
    #FIXME permission check?
    repo = request.POST.get('repo_name')
    if repo:
        tasks.import_image.delay(repo)
        messages.add_message(request, messages.INFO, _('Importing') + \
            ' {}'.format(repo) + _('.  This could take a few minutes.'))
    return redirect('image.views.index')

@login_required
def build_image(request):
    #FIXME permission check?
    path = request.POST.get('path')
    tag = request.POST.get('tag', None)
    if path:
        tasks.build_image.delay(path, tag)
        messages.add_message(request, messages.INFO, _('Building.  This ' \
            'could take a few minutes.'))
    return redirect('image.views.index')
