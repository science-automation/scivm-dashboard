from django.conf.urls import patterns, url

urlpatterns = patterns('crons.views',
    url(r'^$', 'index'),
    url(r'^enable/(?P<cron_id>.*)/$', 'enable_cron'),
    url(r'^disable/(?P<cron_id>.*)/$', 'disable_cron'),
    url(r'^remove/(?P<cron_id>.*)/$', 'remove_cron'),
)
