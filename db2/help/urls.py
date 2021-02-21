from django.urls import path
from . import views

app_name = 'help'
urlpatterns = [
    path('', views.index, name = 'home'),
    path('<int:article_id>/', views.ArticlePageView, name = 'AtrticlePageView'),
]
