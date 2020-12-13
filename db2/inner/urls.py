from django.urls import path
from . import views


app_name="inner"
urlpatterns = [
    path('', views.index, name = 'index'),
    path('ajax-tm/', views.autocomplete_tm, name='autocomplete_tm'),
    path('sales_autocomplete_org/', views.sales_autocomplete_org, name='sales_autocomplete_org'),
    path('clients_autocomplete_org/', views.clients_autocomplete_org, name='clients_autocomplete_org'),
    path('test/', views.test, name = 'test'),
    path('SalesIndividual/', views.SalesIndividual, name = 'SalesIndividual'),
    path('SalesIndividual/<int:edrpou_num>/', views.SalesIndividualFirmShow, name = 'SalesIndividualFirmShow'),
    path('SalesIndividual/<int:edrpou_num>/<int:buyer_code>/', views.SalesIndividualFirmRaw, name = 'SalesIndividualFirmRaw'),
    path('ClientsCompetitorsIndividual/', views.ClientsCompetitorsIndividualSearch, name = 'ClientsCompetitorsIndividualSearch'),
    path('ClientsCompetitorsIndividual/<int:edrpou_num>/', views.ClientsCompetitorsIndividualShow, name = 'ClientsCompetitorsIndividualShow'),
    path('ClientsCompetitorsIndividual/<int:edrpou_num>/<int:seller_code>/', views.ClientsCompetitorsIndividualRaw, name = 'ClientsCompetitorsIndividualRaw'),
    #path('IndividualReport/', views.IndividualReport, name = 'IndividualReport'),
    #path('IndividualReport/<int:edrpou_num>/', views.IndividualReportFirmShow, name = 'IndividualReportFirmShow'),
    #path('IndividualReportRaw/<int:edrpou_num>/<str:gtd_num>/', views.IndividualReportRaw, name = 'IndividualReportRaw'),
    #path('TrademarkReport/', views.TrademarkReportSearch, name = 'TrademarkReportSearch' ),
    #path('TrademarkReport/<str:trademark_name>/', views.TrademarkReportShow, name = 'TrademarkReportShow'),
    #path('TrademarkReport/<str:trademark_name>/<int:edrpou_num>/', views.TrademarkReportRaw, name = 'TrademarkReportRaw'),
    #path('HRKReport/', views.HRKReport, name = 'HRKReport'),
    #path('CompetitorsCatalog/', views.CompetitorsCatalog, name = 'CompetitorsCatalog'),
    #path('CompetitorsCatalog/<int:edrpou_num>', views.CompetitorsCatalogPeriodDetail, name = 'CompetitorsCatalogPeriodDetail'),
    #path('ProductCodesCatalog/', views.ProductCodesCatalog, name = 'ProductCodesCatalog'),
    #path('TnvedGroupCatalog/', views.TnvedGroupCatalog, name = 'TnvedGroupCatalog'),
]
