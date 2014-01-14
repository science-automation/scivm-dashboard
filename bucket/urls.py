from django.conf.urls import patterns, url

urlpatterns = patterns('bucket.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_bucket'),
    url(r'^remove/(?P<bucket_id>.*)/$', 'remove_bucket'),
    url(r'^snapshot/(?P<bucket_id>.*)/$', 'snapshot_bucket'),
)
