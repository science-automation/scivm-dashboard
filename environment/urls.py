from django.conf.urls import patterns, url

urlpatterns = patterns('environment.views',
    url(r'^$', 'index'),
    url(r'^add/$', 'add_environment'),
    url(r'^favorite/(?P<environment_id>.*)/$', 'favorite_environment'),
    url(r'^unfavorite/(?P<environment_id>.*)/$', 'unfavorite_environment'),
    url(r'^clone/(?P<environment_id>.*)/$', 'clone_environment'),
    url(r'^share/(?P<environment_id>.*)/$', 'share_environment'),
    url(r'^edit_info/(?P<environment_id>.*)/$', 'edit_info_environment'),
    url(r'^modify/(?P<environment_id>.*)/$', 'modify_environment'),
    url(r'^remove/(?P<environment_id>.*)/$', 'remove_environment'),
    url(r'^import/$', 'import_image'),
    url(r'^import/$', 'build_image'),
)
