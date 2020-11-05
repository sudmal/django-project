from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify
from time import time


class filter_codes(models.Model):
    product_code  = models.TextField(primary_key=True)
    short_code    = models.TextField(blank=True, null=True)
    description   = models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'filter_codes'
    def __str__(self):
        #String for representing the object (in Admin site etc.)
        return self.product_code

class Competitors(models.Model):
    competitor_code = models.BigIntegerField(primary_key=True)
    competitor_name = models.TextField(blank=True, null=True)
    competitor_surname = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'competitors'


class Country(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'country'


class CreditStaging(models.Model):
    doc_id = models.TextField(blank=True, null=True)
    seller_region = models.TextField(blank=True, null=True)
    seller_rayon = models.TextField(blank=True, null=True)
    seller_edrpou = models.TextField(blank=True, null=True)
    seller_ipn = models.TextField(blank=True, null=True)
    seller_name = models.TextField(blank=True, null=True)
    seller_state = models.TextField(blank=True, null=True)
    buyer_region = models.TextField(blank=True, null=True)
    buyer_rayon = models.TextField(blank=True, null=True)
    buyer_edrpou = models.TextField(blank=True, null=True)
    buyer_ipn = models.TextField(blank=True, null=True)
    buyer_name = models.TextField(blank=True, null=True)
    buyer_state = models.TextField(blank=True, null=True)
    reestr_number = models.TextField(blank=True, null=True)
    nn_number = models.TextField(blank=True, null=True)
    ordering_date = models.DateField(blank=True, null=True)
    registration_date = models.TextField(blank=True, null=True)
    total_pay_cost = models.TextField(blank=True, null=True)
    pdv_summ = models.TextField(blank=True, null=True)
    number_20_percent_count = models.TextField(db_column='20_percent_count', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_7_percent_count = models.TextField(db_column='7_percent_count', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    rk_count = models.TextField(blank=True, null=True)
    correction_cost = models.TextField(blank=True, null=True)
    one_rk_cost = models.TextField(blank=True, null=True)
    product_name = models.TextField(blank=True, null=True)
    product_code = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    count = models.TextField(blank=True, null=True)
    one_product_cost = models.TextField(blank=True, null=True)
    hash = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'credit_staging'


class Exchange(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField(unique=True)
    eur_com = models.FloatField(db_column='EUR-COM', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    eur_nbu = models.FloatField(db_column='EUR-NBU', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    usd_com = models.FloatField(db_column='USD-COM', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    usd_nbu = models.FloatField(db_column='USD-NBU', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    eur_mb_buy = models.FloatField(db_column='EUR-MB-BUY', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    eur_mb_sale = models.FloatField(db_column='EUR-MB-SALE', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'exchange'


class Groupcodes(models.Model):
    id = models.IntegerField(primary_key=True)
    gname = models.CharField(max_length=255, blank=True, null=True)
    gcodes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'groupcodes'


class GtdRecords(models.Model):
    id = models.BigAutoField(primary_key=True)
    product_code = models.BigIntegerField(blank=True, null=True)
    trademark = models.ForeignKey('Trademark', models.DO_NOTHING)
    cost_fact = models.FloatField(blank=True, null=True)
    cost_customs = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    record = models.ForeignKey('Records', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gtd_records'


class NlCredit(models.Model):
    id = models.BigIntegerField(primary_key=True)
    doc_id = models.BigIntegerField(blank=True, null=True)
    reestr_number = models.BigIntegerField(blank=True, null=True)
    seller = models.ForeignKey('NlOrg', on_delete=models.DO_NOTHING, related_name='credit_seller')
    buyer = models.ForeignKey('NlOrg',on_delete=models.DO_NOTHING, related_name='credit_buyer')
    product = models.ForeignKey('NlProduct', models.DO_NOTHING, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    one_product_cost = models.FloatField(blank=True, null=True)
    count = models.FloatField(blank=True, null=True)
    ordering_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nl_credit'


class NlOrg(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField(unique=True, blank=True, null=True)
    edrpou = models.BigIntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'nl_org'


class NlProduct(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nl_product'


class NlReestr(models.Model):
    id = models.BigIntegerField(primary_key=True)
    doc_id = models.BigIntegerField(blank=True, null=True)
    reestr_number = models.BigIntegerField(blank=True, null=True)
    seller = models.ForeignKey(NlOrg,  on_delete=models.DO_NOTHING, related_name='reestr_seller')
    buyer = models.ForeignKey(NlOrg,  on_delete=models.DO_NOTHING, related_name='reestr_buyer')
    product = models.ForeignKey(NlProduct, models.DO_NOTHING, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    one_product_cost = models.FloatField(blank=True, null=True)
    count = models.FloatField(blank=True, null=True)
    ordering_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nl_reestr'


class Organisation(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=2000)
    firm_alias = models.CharField(max_length=2000)
    is_competitor = models.BooleanField()
    edrpou = models.BigIntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'organisation'


class Records(models.Model):
    id = models.BigAutoField(primary_key=True)
    exchange = models.ForeignKey('Exchange', models.DO_NOTHING)
    sender = models.ForeignKey('Sender', models.DO_NOTHING, blank=True, null=True)
    recipient = models.ForeignKey('Organisation', models.DO_NOTHING)
    date = models.DateField()
    gtd_name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'records'


class Sender(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey('Country', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sender'


class SenderTrademark(models.Model):
    sender_name = models.CharField(max_length=255)
    trademark = models.CharField(max_length=255)
    comment = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sender_trademark'


class TmAlias(models.Model):
    sender_name = models.TextField(blank=True, null=True)
    trademark = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tm_alias'


class TnvedGroup(models.Model):
    id = models.BigIntegerField(primary_key=True)
    gname = models.TextField(blank=True, null=True)
    gcodes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tnved_group'


class TnvedMark(models.Model):
    code = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tnved_mark'


class Trademark(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'trademark'
