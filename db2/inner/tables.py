import django_tables2 as tables
from django_tables2 import columns

from .models import ReestrStaging

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
        model = ReestrStaging
        fields = ('num','ordering_date','seller_name','seller_edrpou','buyer_name','buyer_edrpou','product_code','product_name','one_product_cost','count')
        sequence = ('num','ordering_date','seller_name','seller_edrpou','buyer_name','buyer_edrpou','product_code','product_name','one_product_cost','count')
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}
