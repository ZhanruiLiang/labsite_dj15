from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^test_ajax/$', views.make_test_view('test_ajax.html')),
    url(r'^test_upload/$', views.test_upload),
    url(r'^register/$', views.register),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^profile/((?P<userID>\w+)/)?$', views.profile), # for registered user
    url(r'^my/$', views.home), # home page
    url(r'^upload/$', views.upload), # for student
    url(r'^list/((?P<assID>\d\d)/)?$', views.list_submission), # for TA
    url(r'^subm/(?P<submissionID>\w+)/$', views.submission), # for student
    url(r'^grade/$', views.grade), # for TA
    url(r'^post/$', views.post_ass), # for TA
    url(r'^ass/((?P<assID>\w+)/)?$', views.show_ass), # for student and TA
    url(r'^edit/((?P<assID>\w+)/)?$', views.edit_ass), # for student and TA
)
