from django.conf.urls import patterns, url

urlpatterns = patterns('support.views',
    url(r'^$', 'index'),
)
