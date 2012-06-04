from django.conf.urls import patterns, include, url
from reminis.core import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'reminis.views.home', name='home'),
    # url(r'^reminis/', include('reminis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
                       
    url(r'^home/$', views.home),
    url(r'^post/$', views.post),
    url(r'^search/$', views.search),
)
