from django.conf.urls import patterns, include, url
from remenis.core import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from remenis import settings

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
#    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
#    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', views.splash),
    url(r'^(\d+)/$', views.profile),
    url(r'^profile/$', views.profile),
    url(r'^login/$', views.login),
    url(r'^home/$', views.home),
    url(r'^post/$', views.post),
    url(r'^delete/$', views.delete),
    url(r'^searcherror/$', views.searcherror),
    url(r'^messagesent/$', views.messagesent),
    url(r'^story/(\d+)/$', views.story),
    
    url(r'^logout/$', views.logout),
)

urlpatterns += staticfiles_urlpatterns()

admin.autodiscover()

urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),
)

if not settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)