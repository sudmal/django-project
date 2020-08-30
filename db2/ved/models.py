from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify
from time import time


def gen_slug(s):
    new_slug = slugify(s, allow_unicode=True)

    return new_slug + '-' + str(int(time()))


# Create your models here.
class Country(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'country'

class Sender(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(Country, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sender'

class Trademark(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    sender = models.ForeignKey(Sender, models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'trademark'


class Competitors(models.Model):
    competitor_code = models.BigIntegerField(blank=True, null=True)
    competitor_name = models.TextField(blank=True, null=True)
    competitor_surname = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'competitors'


class Organisation(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=2000)
    is_competitor = models.BooleanField()
    edrpou = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'organisation'


class Organization(models.Model):
    title = models.CharField(max_length=200, db_index=True, blank=True, null=True)
    edrpou = models.CharField(max_length=150, db_index=True, blank=True, null=True)

    def __str__(self):
        return self.edrpou


class Gtd(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    product_code = models.BigIntegerField(blank=True, null=True)
    trademark = models.ForeignKey('Trademark', models.DO_NOTHING, blank=True, null=True)
    cost_fact = models.FloatField(blank=True, null=True)
    cost_customs = models.FloatField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gtd'
    

class Records(models.Model):
    id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey('Sender', models.DO_NOTHING, blank=True, null=True)
    recipient = models.ForeignKey(Organisation, models.DO_NOTHING, blank=True, null=True)
    gtd = models.ForeignKey(Gtd, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'records'
        ordering = ['-id']


class Exchange(models.Model):
    date = models.DateField(primary_key=True)
    eur_com = models.TextField(db_column='EUR-COM', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    eur_nbu = models.TextField(db_column='EUR-NBU', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    usd_com = models.TextField(db_column='USD-COM', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    usd_nbu = models.TextField(db_column='USD-NBU', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    eur_mb_buy = models.FloatField(db_column='EUR-MB-BUY', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    eur_mb_sale = models.FloatField(db_column='EUR-MB-SALE', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'exchange'