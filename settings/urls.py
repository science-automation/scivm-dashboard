from django.conf.urls import patterns, url

urlpatterns = patterns('settings.views',
    url(r'^$', 'index'),
)
