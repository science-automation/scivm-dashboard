from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.JobList.as_view(), name="job-list"),
    url(r'^(?P<pk>\d+)/$', views.JobDetail.as_view(), name="job-detail"),
)
