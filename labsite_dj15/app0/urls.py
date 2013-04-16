from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
    # url(r'^test_ajax/$', views.make_test_view('test_ajax.html')),
    # url(r'^test_upload/$', views.test_upload),
    # about accouts
    url(r'^register/$', views.register),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^profile/((?P<userID>\w+)/)?$', views.profile), # for registered user
    url(r'^my/$', views.show_ass), # home page
    # about assignments
    url(r'^ass/((?P<assID>\w+)/)?$', views.show_ass), # view an assignment
    url(r'^edit/((?P<assID>\w+)/)?$', views.edit_ass), # view an assignment, TA only
    url(r'^post/$', views.post_ass), # post an assignment, TA only
    url(r'^delete_ass/(?P<assID>\w+)/', views.delete_ass),
    # about submissions
    # url(r'^ass/(?P<assID>\w+)/list/$', view.ass_list),
    url(r'^subm/(?P<submissionID>\w+)/$', views.submission), # for student, TA
    # AJAX views
    url(r'^upload/$', views.upload), # for student, TA
    url(r'^submission_list/(?P<assID>\w+)/$', views.submission_list),
    url(r'^delete_submission/(?P<submissionID>\w+)/$', views.delete_submission),
    url(r'^grade/$', views.grade), # for TA; AJAX POST
)
