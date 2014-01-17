from django.conf.urls import patterns, url

urlpatterns = patterns('provider.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_provider'),
    url(r'^remove/(?P<provider_id>.*)/$', 'remove_provider'),
)
