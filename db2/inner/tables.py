import django_tables2 as tables
from django_tables2 import columns

from .models import NlReestr

class RecordsSearchTable(tables.Table):
    export_formats = ['csv', 'xls', 'xlsx']
    num = tables.TemplateColumn("{{ row_counter }}")

    #_name = columns.Column(visible=False,exclude_from_export=True)
    #recipient_code = columns.Column(visible=False,exclude_from_export=True)
    #hash = columns.Column(visible=False,exclude_from_export=True)
    #rename columns
    # devenv = tables.Column(verbose_name= 'Development Environment' )
    class Meta:
        export_formats = ['csv', 'xls', 'xlsx']
        model = NlReestr
        #sequence = ('num','ordering_date','seller__name','seller__edrpou','buyer__name','buyer__edrpou','product__product_code','product__name','one_product_cost','count','sum')
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}
