from django.conf.urls import patterns, url

urlpatterns = patterns('bucketfile.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_bucketfile'),
    url(r'^remove/(?P<bucketfile_id>.*)/$', 'remove_bucketfile'),
    url(r'^snapshot/(?P<bucketfile_id>.*)/$', 'snapshot_bucketfile'),
)
