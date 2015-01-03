from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', "dj_pygrooveshark.views.index"),
    url(r'^request/popular/$', "dj_pygrooveshark.views.popular"),
    url(r'^request/search/$', "dj_pygrooveshark.views.search"),
    url(r'^request/stream/$', "dj_pygrooveshark.views.stream"),
)
