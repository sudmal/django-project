from django.urls import path
from . import views


app_name="ved"
urlpatterns = [
    path('', views.index, name = 'index'),
    path('ajax-tm/', views.autocomplete_tm, name='autocomplete_tm'),
    path('ajax-org/', views.autocomplete_org, name='autocomplete_org'),
    path('test/', views.test, name = 'test'),
    path('CompetitorsComparse/', views.CompetitorsComparse, name = 'CompetitorsComparse'),
    path('IndividualReport/', views.IndividualReport, name = 'IndividualReport'),
    path('IndividualReport/<int:edrpou_num>/', views.IndividualReportFirmShow, name = 'IndividualReportFirmShow'),
    path('IndividualReportRaw/<int:edrpou_num>/<str:gtd_num>/', views.IndividualReportRaw, name = 'IndividualReportRaw'),
    path('TrademarkReport/', views.TrademarkReportSearch, name = 'TrademarkReportSearch' ),
    path('TrademarkReport/<str:trademark_name>/', views.TrademarkReportShow, name = 'TrademarkReportShow'),
    path('TrademarkReport/<str:trademark_name>/<int:edrpou_num>/', views.TrademarkReportRaw, name = 'TrademarkReportRaw'),
    path('HRKReport/', views.HRKReport, name = 'HRKReport'),
    path('CompetitorsCatalog/', views.CompetitorsCatalog, name = 'CompetitorsCatalog'),
    path('CompetitorsCatalog/<int:edrpou_num>', views.CompetitorsCatalogPeriodDetail, name = 'CompetitorsCatalogPeriodDetail'),
    path('ProductCodesCatalog/', views.ProductCodesCatalog, name = 'ProductCodesCatalog'),
    path('TnvedGroupCatalog/', views.TnvedGroupCatalog, name = 'TnvedGroupCatalog'),
    path('czCatalog/', views.czCatalog, name = 'czCatalog'),
    path('czTraders/', views.czTraders, name = 'czTraders'),
]
