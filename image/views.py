from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from image.models import Image
from accounts.models import UserProfile
from image.forms import ImageForm, EditImageForm
from scivm import tasks

@login_required
def index(request):
    current_user = request.user
    u = UserProfile.objects.get(id=current_user.id)
    ctx = {
        'private_images': Image.objects.filter(owner__pk=current_user.pk),
        'favorite_images': u.favorite_image.all(),
        'public_images': Image.objects.filter(public=True),
    }
    return render_to_response('image/index.html', ctx,
        context_instance=RequestContext(request))

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
    return render_to_response('image/add_image.html', ctx,
        context_instance=RequestContext(request))

@login_required
def remove_image(request, image_id):
    h = Image.objects.get(id=image_id)
    h.delete()
    messages.add_message(request, messages.INFO, _('Removed') + ' {0}'.format(
        h.name))
    return redirect('image.views.index')

@login_required
def favorite_image(request, image_id):
    """Make an image the favorite of this user
    """
    h = Image.objects.get(id=image_id)
    current_user = request.user
    u = UserProfile.objects.get(id=current_user.id)
    u.favorite_image.add(h)
    # make the image a favorite
    return redirect('image.views.index')

@login_required
def unfavorite_image(request, image_id):
    """Remove an image from favorites
    """
    h = Image.objects.get(id=image_id)
    current_user = request.user
    u = UserProfile.objects.get(id=current_user.id)
    u.favorite_image.remove(h)
    # unstar image
    return redirect('image.views.index')

@login_required
def clone_image(request, image_id):
    h = Image.objects.get(id=image_id)
    # clone the image
    return redirect('image.views.index')

@login_required
def share_image(request, image_id):
    """Share the image with another user. To do: make sure a user owns it
    """
    h = Image.objects.get(id=image_id)
    return redirect('image.views.index')

@login_required
def public_image(request, image_id):
    """Make an image public. To do: make sure a user owns it
    """
    h = Image.objects.get(id=image_id)
    h.public = True
    h.save()
    return redirect('image.views.index')

@login_required
def private_image(request, image_id):
    """Make an image private.  To do: make sure user owns it
    """
    h = Image.objects.get(id=image_id)
    h.public = False
    h.save()
    return redirect('image.views.index')

@login_required
def modify_image(request, image_id):
    h = Image.objects.get(id=image_id)
    # clone the image
    return redirect('image.views.index')

@login_required
def edit_image(request, image_id):
    """Edit the name and description of the enviroment.  Associate images to an image
    """
    h = Image.objects.get(id=image_id)
    current_user = request.user
    u = UserProfile.objects.get(id=current_user.id)
    if request.method == 'POST':
        form = ImageForm(request.POST)
        if form.is_valid():
            ptype = form.save(commit=False)
            ptype.owner = request.user
            ptype.save()
            return redirect(reverse('image.views.index'))
    initial = {
        'name': h.name,
        'description': h.description,
    }
    ctx = {
        'image': h,
        'form': EditImageForm(initial=initial),
    }
    return render_to_response('image/image_details.html', ctx,
        context_instance=RequestContext(request))

@login_required
def import_image(request):
    repo = request.POST.get('repo_name')
    if repo:
        tasks.import_image.delay(repo)
        messages.add_message(request, messages.INFO, _('Importing') + \
            ' {}'.format(repo) + _('.  This could take a few minutes.'))
    return redirect('image.views.index')

@login_required
def build_image(request):
    path = request.POST.get('path')
    tag = request.POST.get('tag', None)
    if path:
        tasks.build_image.delay(path, tag)
        messages.add_message(request, messages.INFO, _('Building.  This ' \
            'could take a few minutes.'))
    return redirect('image.views.index')
