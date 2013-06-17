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
    url(r'^simcheck/(?P<assID>\w+)/', views.show_simcheck),
    # about submissions
    # url(r'^ass/(?P<assID>\w+)/list/$', view.ass_list),
    url(r'^subm/((?P<submissionID>\w+)/)$', views.show_submission), # for student, TA
    url(r'^summary/', views.show_summary),
    # url(r'^assign/(?P<assID>\w+)/$', views.show_assign),
    # AJAX views
    url(r'^upload/$', views.upload), # for student, TA
    url(r'^submission_list/(?P<assID>\w+)/$', views.submission_list),
    url(r'^delete_submission/(?P<submissionID>\w+)/$', views.delete_submission),
    url(r'^grade/$', views.grade), # for TA; AJAX POST
    url(r'^run/(?P<comID>\w+)/$', views.run_prog),
    url(r'^stop/(?P<runID>\w+)/$', views.stop_prog),
    url(r'^interact/(?P<runID>\w+)/$', views.interact_prog),
    url(r'^doassign/(?P<assID>\w+)/$', views.do_assign),
    url(r'^finish/(?P<submissionID>\w+)/', views.finish),
    url(r'^startsimcheck/(?P<assID>\w+)/', views.start_simcheck),
    url(r'^diff/(?P<diffID>\w+)/', views.diff_view),
)
