import django_tables2 as tables
from django_tables2 import columns
import itertools
from .models import NlReestr


class RecordsSearchTable(tables.Table):
    export_formats = ['csv', 'xls', 'xlsx']
    num = tables.TemplateColumn("{{ row_counter }}",verbose_name= '№' )
    curr = tables.TemplateColumn("{{ currency }}",verbose_name= 'Валюта' )
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
        attrs = {'class': 'paleblue'}

class Top100Table(tables.Table):
    counter = tables.Column(verbose_name= '№',empty_values=(), orderable=False)
    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter',
                                   itertools.count(self.page.start_index()))
        return next(self.row_counter)


    export_formats = ['csv', 'xls', 'xlsx']
    seller__name = tables.Column(verbose_name= 'Продавец' )
    product__name = tables.Column(verbose_name= 'Наименование товара' )
    total_count = tables.Column(verbose_name= 'Количество' )
    total_cost = tables.Column(verbose_name= 'Сумма' )
    curr = tables.TemplateColumn("UAH",verbose_name= 'Валюта' )

    class Meta:
        orderable = False
        export_formats = ['csv', 'xls', 'xlsx']
        model = NlReestr
        fields = ('counter','seller__name','product__name','total_count', 'total_cost','curr')
        sequence = ('counter','seller__name','product__name','total_count', 'total_cost','curr')
        attrs = {'class': 'paleblue', 'style':'font-family: Verdana; font-size: 12pt;'}

class Top100Table(tables.Table):
    counter = tables.Column(verbose_name= '№',empty_values=(), orderable=False)
    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter', itertools.count(self.page.start_index()))
        return next(self.row_counter)


    export_formats = ['csv', 'xls', 'xlsx']
    seller__name = tables.Column(verbose_name= 'Продавец' )
    product__name = tables.Column(verbose_name= 'Наименование товара' )
    total_count = tables.Column(verbose_name= 'Количество' )
    total_cost = tables.Column(verbose_name= 'Сумма' )
    curr = tables.TemplateColumn("UAH",verbose_name= 'Валюта' )

    class Meta:
        orderable = False
        export_formats = ['csv', 'xls', 'xlsx']
        model = NlReestr
        fields = ('counter','seller__name','product__name','total_count', 'total_cost','curr')
        sequence = ('counter','seller__name','product__name','total_count', 'total_cost','curr')
        attrs = {'class': 'paleblue', 'style':'font-family: Verdana; font-size: 12pt;'}

