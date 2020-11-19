import django_tables2 as tables
from django_tables2 import columns

from .models import RecordsStaging

class CompetitorsComparsePeriodDetailTable(tables.Table):
    export_formats = ['csv', 'xls', 'xlsx']
    num = tables.TemplateColumn("{{ row_counter }}")

    recipient_name = columns.Column(visible=False,exclude_from_export=True)
    recipient_code = columns.Column(visible=False,exclude_from_export=True)
    hash = columns.Column(visible=False,exclude_from_export=True)
    class Meta:
        export_formats = ['csv', 'xls', 'xlsx']
        model = RecordsStaging
        sequence = ('num','date','gtd','country', 'sender_name', 'recipient_name','recipient_code','product_code','trademark','description','cost_fact','cost_customs')
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}