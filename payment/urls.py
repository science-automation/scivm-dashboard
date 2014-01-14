from django.conf.urls import patterns, url

urlpatterns = patterns('payment.views',
    url(r'^$', 'index'),
)
