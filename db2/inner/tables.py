import django_tables2 as tables
from django_tables2 import columns

from .models import NlReestr

class RecordsSearchTable(tables.Table):
    export_formats = ['csv', 'xls', 'xlsx']
    num = tables.TemplateColumn("{{ row_counter }}",verbose_name= '№' )
    curr = tables.TemplateColumn("{{ currency }}",verbose_name= 'Валюта' )
    #_name = columns.Column(visible=False,exclude_from_export=True)
    #recipient_code = columns.Column(visible=False,exclude_from_export=True)
    #hash = columns.Column(visible=False,exclude_from_export=True)
    #rename columns
    # devenv = tables.Column(verbose_name= 'Development Environment' )
    ordering_date = tables.Column(verbose_name= 'Дата выписки' )
    seller__name = tables.Column(verbose_name= 'Продавец' )
    seller__edrpou = tables.Column(verbose_name= 'ЕДРПОУ продавца' )
    buyer__name = tables.Column(verbose_name= 'Покупатель' )
    buyer__edrpou = tables.Column(verbose_name= 'ЕДРПОУ покупателя' )
    product__product_code = tables.Column(verbose_name= 'Код УКТВЭД' )
    product__name = tables.Column(verbose_name= 'Наименование товара' )
    cost = tables.Column(verbose_name= 'Цена' )
    count = tables.Column(verbose_name= 'Количество' )
    total_cost = tables.Column(verbose_name= 'Сумма' )

    class Meta:
        export_formats = ['csv', 'xls', 'xlsx']
        model = NlReestr
        fields = ('num','ordering_date','seller__name','seller__edrpou','buyer__name','buyer__edrpou','product__product_code','product__name','cost','count', 'total_cost', 'curr')
        sequence = ('num','ordering_date','seller__name','seller__edrpou','buyer__name','buyer__edrpou','product__product_code','product__name','cost','count', 'total_cost', 'curr')
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}
