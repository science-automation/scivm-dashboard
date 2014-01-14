from django.conf.urls import patterns, url

urlpatterns = patterns('environment.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_environment'),
    url(r'^remove/(?P<environment_id>.*)/$', 'remove_environment'),
)
