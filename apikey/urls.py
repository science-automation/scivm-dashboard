from django.conf.urls import patterns, url

urlpatterns = patterns('apikey.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_apikey'),
    url(r'^edit/(?P<apikey_id>.*)/$', 'edit_apikey'),
    url(r'^enable/(?P<apikey_id>.*)/$', 'enable_apikey'),
    url(r'^disable/(?P<apikey_id>.*)/$', 'disable_apikey'),
    url(r'^remove/(?P<apikey_id>.*)/$', 'remove_apikey'),
)
