import django_tables2 as tables
from django_tables2 import columns

from .models import RecordsStaging

class CompetitorsComparsePeriodDetailTable(tables.Table):
    export_formats = ['csv', 'xls', 'xlsx']
    num = tables.TemplateColumn("{{ row_counter }}")

    recipient_name = columns.Column(visible=False,exclude_from_export=True)
    recipient_code = columns.Column(visible=False,exclude_from_export=True)
    date = tables.Column(verbose_name= 'Дата')
    gtd = tables.Column(verbose_name= 'ГТД')
    country = tables.Column(verbose_name= 'Страна')
    sender_name = tables.Column(verbose_name= 'Отправитель')
    product_code = tables.Column(verbose_name= 'ТНВЭД')
    trademark = tables.Column(verbose_name= 'Торговая марка')
    description = tables.Column(verbose_name= 'Описание')
    cost_fact = tables.Column(verbose_name= 'Фактурная стоимость')
    cost_customs = tables.Column(verbose_name= 'Таможенная стоимость')
    hash = columns.Column(visible=False,exclude_from_export=True)
    #rename columns
    # devenv = tables.Column(verbose_name= 'Development Environment' )
    class Meta:
        export_formats = ['csv', 'xls', 'xlsx']
        model = RecordsStaging
        sequence = ('num','date','gtd','country', 'sender_name', 'recipient_name','recipient_code','product_code','trademark','description','cost_fact','cost_customs')
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}
     