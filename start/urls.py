from django.conf.urls import patterns, url

urlpatterns = patterns('start.views',
    url(r'^$', 'index'),
)
