from django.db import models


class Competitors(models.Model):
    competitor_code = models.BigIntegerField(primary_key=True)
    competitor_name = models.TextField(blank=True, null=True)
    competitor_surname = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'competitors'

