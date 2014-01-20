from django.conf.urls import patterns, url

urlpatterns = patterns('image.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_image'),
    url(r'^favorite/(?P<image_id>.*)/$', 'favorite_image'),
    url(r'^unfavorite/(?P<image_id>.*)/$', 'unfavorite_image'),
    url(r'^clone/(?P<image_id>.*)/$', 'clone_image'),
    url(r'^share/(?P<image_id>.*)/$', 'share_image'),
    url(r'^edit/(?P<image_id>.*)/$', 'edit_image'),
    url(r'^modify/(?P<image_id>.*)/$', 'modify_image'),
    url(r'^remove/(?P<image_id>.*)/$', 'remove_image'),
    url(r'^public/(?P<image_id>.*)/$', 'public_image'),
    url(r'^private/(?P<image_id>.*)/$', 'private_image'),
    url(r'^import/$', 'import_image'),
    url(r'^import/$', 'build_image'),
)
