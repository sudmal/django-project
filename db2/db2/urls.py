from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('help/',include('help.urls',namespace='help'), name = 'help'),
    path('ved/',include('ved.urls',namespace='ved'), name = 'ved'),
    path('inner/',include('inner.urls',namespace='inner'), name = 'inner'),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]