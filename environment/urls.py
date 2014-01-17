from django.conf.urls import patterns, url

urlpatterns = patterns('environment.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_environment'),
    url(r'^star/(?P<environment_id>.*)/$', 'star_environment'),
    url(r'^remove/(?P<environment_id>.*)/$', 'remove_environment'),
    url(r'^import/$', 'import_image'),
    url(r'^import/$', 'build_image'),
)
