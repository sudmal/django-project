from django.db import models
from django.db.models.signals import post_save, pre_delete


# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.fields import BooleanField
import tinymce
from tinymce.models import HTMLField

class ArticlePage(models.Model):
    Title=models.CharField(max_length=50, blank=False, null=False)
    CreationDate=models.DateTimeField(verbose_name="Created", name="Created", auto_now=True)
    #Text=HTMLField()
    Text=tinymce.models.HTMLField(max_length=65534, blank=False, null=False)
    def __str__(self):
        return self.Title
