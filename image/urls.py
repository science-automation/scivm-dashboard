from django.conf.urls import patterns, url

urlpatterns = patterns('image.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_image'),
    url(r'^remove/(?P<image_id>.*)/$', 'remove_image'),
    url(r'^import/$', 'import_image'),
    url(r'^import/$', 'build_image'),
)
