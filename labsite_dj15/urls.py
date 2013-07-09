from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()
# from dajaxice.core import dajaxice_autodiscover, dajaxice_config
# dajaxice_autodiscover()
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'labsite_dj15.views.home', name='home'),
    # url(r'^labsite_dj15/', include('labsite_dj15.foo.urls')),
    url(r'^m/', include('labsite_dj15.app0.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
