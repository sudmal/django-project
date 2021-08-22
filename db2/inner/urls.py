from django.urls import path
from . import views


app_name="inner"
urlpatterns = [
    path('', views.index, name = 'index'),
    path('ajax-tm/', views.autocomplete_tm, name='autocomplete_tm'),
    path('sales_autocomplete_org/', views.sales_autocomplete_org, name='sales_autocomplete_org'),
    path('clients_autocomplete_org/', views.clients_autocomplete_org, name='clients_autocomplete_org'),
    path('purchases_autocomplete_org/', views.purchases_autocomplete_org, name='purchases_autocomplete_org'),
    path('test/', views.test, name = 'test'),
    path('SalesIndividual/', views.SalesIndividual, name = 'SalesIndividual'),
    path('SalesIndividual/<int:edrpou_num>/', views.SalesIndividualFirmShow, name = 'SalesIndividualFirmShow'),
    path('SalesIndividual/<int:edrpou_num>/<int:buyer_code>/', views.SalesIndividualFirmRaw, name = 'SalesIndividualFirmRaw'),
    path('ClientsCompetitorsIndividual/', views.ClientsCompetitorsIndividualSearch, name = 'ClientsCompetitorsIndividualSearch'),
    path('ClientsCompetitorsIndividual/<int:edrpou_num>/', views.ClientsCompetitorsIndividualShow, name = 'ClientsCompetitorsIndividualShow'),
    path('ClientsCompetitorsIndividual/<int:edrpou_num>/<int:seller_code>/', views.ClientsCompetitorsIndividualRaw, name = 'ClientsCompetitorsIndividualRaw'),
    path('PurchasesIndividual/', views.PurchasesIndividualSearch, name = 'PurchasesIndividualSearch'),
    path('PurchasesIndividual/<int:edrpou_num>/', views.PurchasesIndividualFirmShow, name = 'PurchasesIndividualFirmShow'),
    path('PurchasesIndividual/<int:edrpou_num>/<int:seller_code>/', views.PurchasesIndividualFirmRaw, name = 'PurchasesIndividualFirmRaw'),
    path('SalesCompetitorsComparse/', views.SalesCompetitorsComparse, name = 'SalesCompetitorsComparse'),
    path('ClientsCompetitorsComparse/', views.ClientsCompetitorsComparse, name = 'ClientsCompetitorsComparse'),
    path('CompetitorsCatalog/', views.CompetitorsCatalog, name = 'CompetitorsCatalog'),
    path('RecordsSearch/', views.RecordsSearch, name = 'RecordsSearch'),
    path('topSales/',views.topSales, name='topSales'),
    path('topSales/<int:edrpou_num>/',views.topSalesFirmShow, name='topSalesFirmShow'), 
]
