from django.db import models


class Competitors(models.Model):
    competitor_code = models.BigIntegerField(primary_key=True)
    competitor_name = models.TextField(blank=True, null=True)
    competitor_surname = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'competitors'

class Organisation(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=2000)
    firm_alias = models.CharField(max_length=2000)
    is_competitor = models.BooleanField()
    edrpou = models.BigIntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'organisation'

class CreditStaging(models.Model):
    doc_id = models.TextField(blank=True, null=True)
    seller_region = models.TextField(blank=True, null=True)
    seller_rayon = models.TextField(blank=True, null=True)
    seller_edrpou = models.BigIntegerField(blank=True, null=True)
    seller_ipn = models.TextField(blank=True, null=True)
    seller_name = models.TextField(blank=True, null=True)
    seller_state = models.TextField(blank=True, null=True)
    buyer_region = models.TextField(blank=True, null=True)
    buyer_rayon = models.TextField(blank=True, null=True)
    buyer_edrpou = models.BigIntegerField(blank=True, null=True)
    buyer_ipn = models.TextField(blank=True, null=True)
    buyer_name = models.TextField(blank=True, null=True)
    buyer_state = models.TextField(blank=True, null=True)
    reestr_number = models.BigIntegerField(blank=True, null=True)
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
    date = models.DateField(unique=True)
    eur_com = models.FloatField(db_column='EUR-COM', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    eur_nbu = models.FloatField(db_column='EUR-NBU', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    usd_com = models.FloatField(db_column='USD-COM', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    usd_nbu = models.FloatField(db_column='USD-NBU', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    eur_mb_buy = models.FloatField(db_column='EUR-MB-BUY', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    eur_mb_sale = models.FloatField(db_column='EUR-MB-SALE', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    id = models.BigAutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'exchange'

class NlCredit(models.Model):
    id = models.BigAutoField(primary_key=True)
    doc_id = models.BigIntegerField(blank=True, null=True)
    reestr_number = models.BigIntegerField(blank=True, null=True)
    seller = models.ForeignKey('NlOrg', models.DO_NOTHING, related_name='credit_seller', blank=True, null=True)
    buyer = models.ForeignKey('NlOrg', models.DO_NOTHING, related_name='credit_buyler', blank=True, null=True)
    product = models.ForeignKey('NlProduct', models.DO_NOTHING, blank=True, null=True)
    exchange = models.ForeignKey('Exchange', models.DO_NOTHING, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    one_product_cost = models.FloatField(blank=True, null=True)
    count = models.FloatField(blank=True, null=True)
    ordering_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nl_credit'


class NlOrg(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    edrpou = models.BigIntegerField(unique=True)
    class_field = models.ForeignKey('NlOrgClass', models.DO_NOTHING, db_column='class')  # Field renamed because it was a Python reserved word.

    class Meta:
        managed = False
        db_table = 'nl_org'


class NlOrgClass(models.Model):
    name = models.TextField(unique=True)
    class Meta:
        managed = False
        db_table = 'nl_org_class'


class NlProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    product_code = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nl_product'


class NlReestr(models.Model):
    id = models.BigAutoField(primary_key=True)
    doc_id = models.BigIntegerField(blank=True, null=True)
    reestr_number = models.BigIntegerField(blank=True, null=True)
    seller = models.ForeignKey(NlOrg, models.DO_NOTHING, related_name='reestr_seller', blank=True, null=True)
    buyer = models.ForeignKey(NlOrg, models.DO_NOTHING, related_name='reestr_buyer', blank=True, null=True)
    product = models.ForeignKey(NlProduct, models.DO_NOTHING, blank=True, null=True)
    exchange = models.ForeignKey('Exchange', models.DO_NOTHING, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    one_product_cost = models.FloatField(blank=True, null=True)
    count = models.FloatField(blank=True, null=True)
    ordering_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nl_reestr'

class ReestrStaging(models.Model):
    doc_id = models.TextField(blank=True, null=True)
    seller_region = models.TextField(blank=True, null=True)
    seller_rayon = models.TextField(blank=True, null=True)
    seller_edrpou = models.BigIntegerField(blank=True, null=True)
    seller_ipn = models.TextField(blank=True, null=True)
    seller_name = models.TextField(blank=True, null=True)
    seller_state = models.TextField(blank=True, null=True)
    buyer_region = models.TextField(blank=True, null=True)
    buyer_rayon = models.TextField(blank=True, null=True)
    buyer_edrpou = models.BigIntegerField(blank=True, null=True)
    buyer_ipn = models.TextField(blank=True, null=True)
    buyer_name = models.TextField(blank=True, null=True)
    buyer_state = models.TextField(blank=True, null=True)
    reestr_number = models.BigIntegerField(blank=True, null=True)
    nn_number = models.TextField(blank=True, null=True)
    ordering_date = models.TextField(blank=True, null=True)
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
        db_table = 'reestr_staging'


class NlFilter(models.Model):
    edrpou = models.BigIntegerField(primary_key=True)
    type = models.TextField()

    class Meta:
        managed = False
        db_table = 'nl_filter'
    def __str__(self):
        return str(self.edrpou)+" ("+str(self.type)+')'


class Youscore(models.Model):
    request = models.TextField(unique=True, blank=True, null=True)
    jsonreply = models.TextField(blank=True, null=True)
    id = models.BigAutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'youscore'
