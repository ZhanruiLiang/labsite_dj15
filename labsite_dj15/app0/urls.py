from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^test/$', views.test),
    url(r'^register/$', views.register),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^profile/((?P<userID>\w+)/)?$', views.profile),
    url(r'^my/$', views.home),
    url(r'^upload/$', views.upload),
    url(r'^list/((?P<weeknum>\d\d)/)?$', views.list_submission),
    url(r'^subm/(?P<submissionID>\w+)/$', views.submission),
    url(r'^grade/$', views.grade),
)
