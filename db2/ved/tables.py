import django_tables2 as tables
from .models import RecordsStaging

class CompetitorsComparsePeriodDetailTable(tables.Table):
    class Meta:
        model = RecordsStaging
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}