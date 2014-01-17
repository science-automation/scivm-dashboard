from django.conf.urls import patterns, url

urlpatterns = patterns('bucketstore.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_bucketstore'),
    url(r'^remove/(?P<bucketstore_id>.*)/$', 'remove_bucketstore'),
    url(r'^snapshot/(?P<bucketstore_id>.*)/$', 'snapshot_bucketstore'),
)
