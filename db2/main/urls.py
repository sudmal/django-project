from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name = 'home'),
    path('login', views.login_user, name = 'login'),
    path('logout', views.logout_user, name = 'logout'),
    path('about', views.about, name = 'about'),
    path('ProfileUpdate/', views.ProfileUpdate, name = 'ProfileUpdate'),
    path('FirmInfo/<int:edrpou_num>/', views.FirmInfo, name = 'FirmInfo'),
]
