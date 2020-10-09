from django.urls import path
from . import views


app_name="ved"
urlpatterns = [
    path('', views.index, name = 'index'),
    path('test/', views.test, name = 'test'),
    path('CompetitorsComparse/', views.CompetitorsComparse, name = 'CompetitorsComparse'),
    path('IndividualReport/', views.IndividualReport, name = 'IndividualReport'),
    path('IndividualReport/<int:edrpou_num>/', views.IndividualReportFirmShow, name = 'IndividualReportFirmShow'),
    path('IndividualReportRaw/<int:edrpou_num>/<str:gtd_num>/', views.IndividualReportRaw, name = 'IndividualReportRaw'),
    path('TrademarkReport/', views.TrademarkReportSearch, name = 'TrademarkReportSearch' ),
    path('TrademarkReport/<str:trademark_name>/', views.TrademarkReportShow, name = 'TrademarkReportShow'),
]
