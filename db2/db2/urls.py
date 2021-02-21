from typing import Pattern
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from filebrowser.sites import site


urlpatterns = [
    path('admin/filebrowser/', site.urls),
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('help/',include('help.urls',namespace='help'), name = 'help'),
    path('ved/',include('ved.urls',namespace='ved'), name = 'ved'),
    path('inner/',include('inner.urls',namespace='inner'), name = 'inner'),
]
#if settings.DEBUG:
#    import debug_toolbar
#    urlpatterns += [
#        url(r'^__debug__/', include(debug_toolbar.urls)),
#    ]