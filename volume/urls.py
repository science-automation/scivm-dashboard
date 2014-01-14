from django.conf.urls import patterns, url

urlpatterns = patterns('volume.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_volume'),
    url(r'^remove/(?P<volume_id>.*)/$', 'remove_volume'),
    url(r'^snapshot/(?P<volume_id>.*)/$', 'snapshot_volume'),
)
